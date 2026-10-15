"""Supabase store via PostgREST. Uses the service-role key (server-side secret, never sent to the
browser); all tables have RLS on with no policies, so only this backend can reach them.

Reads use resource embedding (scenarios + scenario_values); writes go through the
create_scenario / update_scenario SQL functions so a scenario and its values are saved atomically.
Every query is scoped by session_id."""
import httpx

from ..core.parameters import diff_with_rows
from .base import ScenarioLimitError, ScenarioNameTaken, StorageUnavailable

_SELECT = "id,name,updated_at,scenario_values(parameter_code,value)"


def _row(r: dict) -> dict:
    return {
        "id": r["id"],
        "name": r["name"],
        "inputs": {v["parameter_code"]: v["value"] for v in r["scenario_values"]},
        "updatedAt": r["updated_at"],
    }


class SupabaseScenarioStore:
    def __init__(self, url: str, service_key: str, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=10.0)
        self._base = f"{url.rstrip('/')}/rest/v1"
        self._headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}"}

    def _call(self, method: str, path: str, params: dict | None = None, headers: dict | None = None, **kw):
        try:
            resp = self._client.request(
                method, f"{self._base}/{path}", params=params, headers={**self._headers, **(headers or {})}, **kw
            )
        except httpx.HTTPError as exc:
            raise StorageUnavailable(str(exc)) from exc
        if resp.status_code >= 400:
            raise StorageUnavailable(f"supabase {resp.status_code}")
        return resp

    def verify_parameters(self) -> None:
        """Fail fast if the database `parameters` table differs from the code catalog."""
        rows = self._call("GET", "parameters", {"select": "*"}).json()
        problems = diff_with_rows(rows)
        if problems:
            raise RuntimeError("parameters table out of sync with backend catalog: " + "; ".join(problems))

    def _get(self, session_id: str, scenario_id: str) -> dict | None:
        rows = self._call(
            "GET", "scenarios", {"id": f"eq.{scenario_id}", "session_id": f"eq.{session_id}", "select": _SELECT}
        ).json()
        return _row(rows[0]) if rows else None

    def _write(self, fn: str, payload: dict) -> str | None:
        """Call a write function; returns the scenario id, or None for not_found."""
        result = self._call("POST", f"rpc/{fn}", json=payload).json()
        status = result["status"]
        if status == "ok":
            return result["id"]
        if status == "limit":
            raise ScenarioLimitError
        if status == "name_taken":
            raise ScenarioNameTaken
        return None

    def list(self, session_id):
        rows = self._call("GET", "scenarios", {"session_id": f"eq.{session_id}", "select": _SELECT, "order": "updated_at.desc"}).json()
        return [_row(r) for r in rows]

    def create(self, session_id, name, inputs):
        new_id = self._write("create_scenario", {"p_session": session_id, "p_name": name, "p_values": inputs})
        return self._get(session_id, new_id)

    def update(self, session_id, scenario_id, name, inputs):
        found = self._write(
            "update_scenario", {"p_session": session_id, "p_id": scenario_id, "p_name": name, "p_values": inputs}
        )
        return self._get(session_id, found) if found else None

    def delete(self, session_id, scenario_id):
        resp = self._call(
            "DELETE", "scenarios", {"id": f"eq.{scenario_id}", "session_id": f"eq.{session_id}", "select": "id"},
            headers={"Prefer": "return=representation"},
        )
        return len(resp.json()) > 0
