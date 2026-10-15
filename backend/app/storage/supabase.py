"""Supabase store via PostgREST. Uses the service-role key (server-side secret, never sent to the
browser); the table has RLS enabled with no policies, so only this backend can reach it.
Every query is filtered by session_id."""
import httpx

from .base import MAX_SCENARIOS_PER_SESSION, ScenarioLimitError, StorageUnavailable

_COLS = "id,name,inputs,updated_at"


def _row(r: dict) -> dict:
    return {"id": r["id"], "name": r["name"], "inputs": r["inputs"], "updatedAt": r["updated_at"]}


class SupabaseScenarioStore:
    def __init__(self, url: str, service_key: str, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=10.0)
        self._base = f"{url.rstrip('/')}/rest/v1/scenarios"
        self._headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}"}

    def _call(self, method: str, params: dict, **kw) -> httpx.Response:
        try:
            resp = self._client.request(method, self._base, params=params, headers={**self._headers, **kw.pop("headers", {})}, **kw)
        except httpx.HTTPError as exc:
            raise StorageUnavailable(str(exc)) from exc
        if resp.status_code >= 400:
            raise StorageUnavailable(f"supabase {resp.status_code}")
        return resp

    def list(self, session_id):
        resp = self._call("GET", {"session_id": f"eq.{session_id}", "select": _COLS, "order": "updated_at.desc"})
        return [_row(r) for r in resp.json()]

    def create(self, session_id, name, inputs):
        if len(self.list(session_id)) >= MAX_SCENARIOS_PER_SESSION:
            raise ScenarioLimitError
        resp = self._call(
            "POST", {"select": _COLS},
            json={"session_id": session_id, "name": name, "inputs": inputs},
            headers={"Prefer": "return=representation"},
        )
        return _row(resp.json()[0])

    def update(self, session_id, scenario_id, name, inputs):
        resp = self._call(
            "PATCH", {"id": f"eq.{scenario_id}", "session_id": f"eq.{session_id}", "select": _COLS},
            json={"name": name, "inputs": inputs},
            headers={"Prefer": "return=representation"},
        )
        rows = resp.json()
        return _row(rows[0]) if rows else None

    def delete(self, session_id, scenario_id):
        resp = self._call(
            "DELETE", {"id": f"eq.{scenario_id}", "session_id": f"eq.{session_id}", "select": "id"},
            headers={"Prefer": "return=representation"},
        )
        return len(resp.json()) > 0
