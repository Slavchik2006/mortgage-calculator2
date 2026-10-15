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
SCN = "11111111-1111-1111-1111-111111111111"


def _row(name="n"):
    return {"id": SCN, "name": name, "updated_at": "t",
            "scenario_values": [{"parameter_code": k, "value": v} for k, v in BODY.items()]}


class FakePostgrest:
    """Records requests; replies per path."""

    def __init__(self, rpc_status="ok", rows=None):
        self.requests, self.rpc_status, self.rows = [], rpc_status, [_row()] if rows is None else rows

    def __call__(self, req: httpx.Request) -> httpx.Response:
        self.requests.append(req)
        path = req.url.path
        if path.endswith("/rpc/create_scenario") or path.endswith("/rpc/update_scenario"):
            return httpx.Response(200, json={"status": self.rpc_status, "id": SCN})
        if req.method == "DELETE":
            return httpx.Response(200, json=[{"id": SCN}] if self.rows else [])
        return httpx.Response(200, json=self.rows)


def _supabase_client(handler):
    store = SupabaseScenarioStore("https://x.supabase.co", "SERVICEKEY", httpx.Client(transport=httpx.MockTransport(handler)))
    return TestClient(create_app(store))


def test_supabase_list_maps_values_to_inputs_and_scopes_by_session():
    fake = FakePostgrest()
    c, h = _supabase_client(fake), sid()
    got = c.get("/api/v1/scenarios", headers=h).json()
    assert got == [{"id": SCN, "name": "n", "inputs": BODY, "updatedAt": "t"}]
    req = fake.requests[0]
    assert req.headers["apikey"] == "SERVICEKEY"
    assert req.url.params["session_id"] == f"eq.{h['X-Session-Id']}"
    assert "scenario_values(parameter_code,value)" in req.url.params["select"]


def test_supabase_create_uses_atomic_rpc_with_session_and_all_six_values():
    fake = FakePostgrest()
    c, h = _supabase_client(fake), sid()
    r = c.post("/api/v1/scenarios", json={"name": "n", "inputs": BODY}, headers=h)
    assert r.status_code == 201 and r.json()["id"] == SCN
    rpc = next(q for q in fake.requests if q.url.path.endswith("/rpc/create_scenario"))
    payload = json.loads(rpc.content)
    assert payload["p_session"] == h["X-Session-Id"] and payload["p_name"] == "n"
    assert set(payload["p_values"]) == set(BODY)


@pytest.mark.parametrize("status", ["limit", "name_taken"])
def test_supabase_create_conflicts(status):
    c = _supabase_client(FakePostgrest(rpc_status=status))
    assert c.post("/api/v1/scenarios", json={"name": "n", "inputs": BODY}, headers=sid()).status_code == 409


def test_supabase_update_statuses():
    h, url = sid(), f"/api/v1/scenarios/{SCN}"
    body = {"name": "n", "inputs": BODY}
    assert _supabase_client(FakePostgrest()).put(url, json=body, headers=h).status_code == 200
    assert _supabase_client(FakePostgrest(rpc_status="not_found")).put(url, json=body, headers=h).status_code == 404
    assert _supabase_client(FakePostgrest(rpc_status="name_taken")).put(url, json=body, headers=h).status_code == 409


def test_supabase_delete():
    h, url = sid(), f"/api/v1/scenarios/{SCN}"
    assert _supabase_client(FakePostgrest()).delete(url, headers=h).status_code == 204
    assert _supabase_client(FakePostgrest(rows=[])).delete(url, headers=h).status_code == 404


def test_supabase_down_gives_503():
    def handler(req):
        raise httpx.ConnectError("boom")

    c = _supabase_client(handler)
    assert c.get("/api/v1/scenarios", headers=sid()).status_code == 503
    assert c.post("/api/v1/calculate", json=BODY).status_code == 200  # calculation has no DB dependency


def test_memory_duplicate_name_is_409(client):
    h = sid()
    assert client.post("/api/v1/scenarios", json={"name": "A", "inputs": BODY}, headers=h).status_code == 201
    r = client.post("/api/v1/scenarios", json={"name": "A", "inputs": BODY}, headers=h)
    assert r.status_code == 409 and "already exists" in r.json()["error"]
    other = client.post("/api/v1/scenarios", json={"name": "B", "inputs": BODY}, headers=h).json()["id"]
    assert client.put(f"/api/v1/scenarios/{other}", json={"name": "A", "inputs": BODY}, headers=h).status_code == 409
    assert client.put(f"/api/v1/scenarios/{other}", json={"name": "B", "inputs": BODY}, headers=h).status_code == 200
    assert client.post("/api/v1/scenarios", json={"name": "A", "inputs": BODY}, headers=sid()).status_code == 201


def test_frontend_served_same_origin(client):
    r = client.get("/")
    assert r.status_code == 200 and "Calculate" in r.text
    assert client.get("/src/main.js").status_code == 200
    assert client.get("/api/v1/health").status_code == 200  # API routes win over the static mount
