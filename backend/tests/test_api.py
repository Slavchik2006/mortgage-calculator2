import json
import uuid

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.storage.memory import MemoryScenarioStore
from app.storage.supabase import SupabaseScenarioStore

BODY = dict(price="300000", downPayment="60000", annualRate="4.5", termYears="30", annualTax="3000", annualInsurance="")


@pytest.fixture
def client():
    return TestClient(create_app(MemoryScenarioStore()))


def sid():
    return {"X-Session-Id": str(uuid.uuid4())}


def test_health(client):
    assert client.get("/api/v1/health").json() == {"status": "ok"}


def test_calculate_ok(client):
    r = client.post("/api/v1/calculate", json=BODY)
    assert r.status_code == 200
    d = r.json()
    assert d["summary"]["principal"] == "240000"
    assert d["summary"]["monthlyTax"] == "250"
    assert d["summary"]["monthlyInsurance"] == "0"
    assert len(d["schedule"]) == 360
    assert d["schedule"][-1]["balance"] == "0"
    assert d["schedule"][0]["interest"] == "900"
    assert d["summary"]["monthlyPI"].startswith("1216.04")


def test_calculate_max_cap_exact_strings(client):
    r = client.post("/api/v1/calculate", json=dict(BODY, price="1000000000000", downPayment="0", annualRate="0", termYears="40"))
    assert r.status_code == 200
    assert r.json()["summary"]["principal"] == "1000000000000"
    assert r.json()["schedule"][-1]["balance"] == "0"


def test_calculate_422_field_errors(client):
    r = client.post("/api/v1/calculate", json=dict(BODY, annualRate="26", downPayment="300000"))
    assert r.status_code == 422
    assert set(r.json()["errors"]) == {"annualRate", "downPayment"}


def test_calculate_empty_object_is_422_required(client):
    r = client.post("/api/v1/calculate", json={})
    assert r.status_code == 422 and "price" in r.json()["errors"]


def test_calculate_400_malformed(client):
    assert client.post("/api/v1/calculate", content="{nope", headers={"content-type": "application/json"}).status_code == 400
    assert client.post("/api/v1/calculate", json=dict(BODY, price=300000)).status_code == 400  # number, not string
    assert client.post("/api/v1/calculate", json=[1]).status_code == 400


def test_field_length_limit(client):
    r = client.post("/api/v1/calculate", json=dict(BODY, price="1" * 40))
    assert r.status_code == 422 and "price" in r.json()["errors"]


def test_scenarios_need_session_id(client):
    assert client.get("/api/v1/scenarios").status_code == 400
    assert client.get("/api/v1/scenarios", headers={"X-Session-Id": "abc"}).status_code == 400


def test_scenario_crud_and_isolation(client):
    a, b = sid(), sid()
    r = client.post("/api/v1/scenarios", json={"name": "  House  ", "inputs": BODY}, headers=a)
    assert r.status_code == 201 and r.json()["name"] == "House"
    scn = r.json()["id"]
    assert [s["id"] for s in client.get("/api/v1/scenarios", headers=a).json()] == [scn]
    assert client.get("/api/v1/scenarios", headers=b).json() == []
    assert client.put(f"/api/v1/scenarios/{scn}", json={"name": "x", "inputs": BODY}, headers=b).status_code == 404
    assert client.delete(f"/api/v1/scenarios/{scn}", headers=b).status_code == 404
    r = client.put(f"/api/v1/scenarios/{scn}", json={"name": "Renamed", "inputs": BODY}, headers=a)
    assert r.status_code == 200 and r.json()["name"] == "Renamed"
    assert client.delete(f"/api/v1/scenarios/{scn}", headers=a).status_code == 204
    assert client.get("/api/v1/scenarios", headers=a).json() == []


def test_scenario_validation_and_name(client):
    h = sid()
    r = client.post("/api/v1/scenarios", json={"name": "ok", "inputs": dict(BODY, termYears="0")}, headers=h)
    assert r.status_code == 422 and "termYears" in r.json()["errors"]
    r = client.post("/api/v1/scenarios", json={"name": "   ", "inputs": BODY}, headers=h)
    assert r.status_code == 422 and "name" in r.json()["errors"]
    assert client.post("/api/v1/scenarios", json={"name": "x" * 61, "inputs": BODY}, headers=h).status_code == 422


def test_scenario_limit(client):
    h = sid()
    for i in range(50):
        assert client.post("/api/v1/scenarios", json={"name": f"s{i}", "inputs": BODY}, headers=h).status_code == 201
    assert client.post("/api/v1/scenarios", json={"name": "extra", "inputs": BODY}, headers=h).status_code == 409


def test_bad_scenario_id_is_400(client):
    assert client.delete("/api/v1/scenarios/not-a-uuid", headers=sid()).status_code == 400


# ---- Supabase store against a mocked PostgREST ----
def _supabase_client(handler):
    store = SupabaseScenarioStore("https://x.supabase.co", "SERVICEKEY", httpx.Client(transport=httpx.MockTransport(handler)))
    return TestClient(create_app(store))


def test_supabase_store_scopes_by_session_and_uses_key():
    seen = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        if req.method == "GET":
            return httpx.Response(200, json=[{"id": "i1", "name": "n", "inputs": BODY, "updated_at": "t"}])
        return httpx.Response(200, json=[{"id": "i1", "name": "n", "inputs": json.loads(req.content)["inputs"], "updated_at": "t"}])

    c = _supabase_client(handler)
    h = sid()
    assert c.get("/api/v1/scenarios", headers=h).json()[0]["updatedAt"] == "t"
    r = c.post("/api/v1/scenarios", json={"name": "n", "inputs": BODY}, headers=h)
    assert r.status_code == 201
    for req in seen:
        assert req.headers["apikey"] == "SERVICEKEY"
        assert req.url.params.get("session_id") == f"eq.{h['X-Session-Id']}" or req.method == "POST"
    assert json.loads(seen[-1].content)["session_id"] == h["X-Session-Id"]


def test_supabase_down_gives_503():
    def handler(req):
        raise httpx.ConnectError("boom")

    c = _supabase_client(handler)
    assert c.get("/api/v1/scenarios", headers=sid()).status_code == 503
    assert c.post("/api/v1/calculate", json=BODY).status_code == 200  # calculation has no DB dependency


def test_supabase_update_delete_missing_row_is_404():
    c = _supabase_client(lambda req: httpx.Response(200, json=[]))
    h, i = sid(), str(uuid.uuid4())
    assert c.put(f"/api/v1/scenarios/{i}", json={"name": "n", "inputs": BODY}, headers=h).status_code == 404
    assert c.delete(f"/api/v1/scenarios/{i}", headers=h).status_code == 404


def test_frontend_served_same_origin(client):
    r = client.get("/")
    assert r.status_code == 200 and "Calculate" in r.text
    assert client.get("/src/main.js").status_code == 200
    assert client.get("/api/v1/health").status_code == 200  # API routes win over the static mount
