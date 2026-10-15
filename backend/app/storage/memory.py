"""In-memory store: default for development and tests. Mirrors the database rules
(unique name per session, 50 per session)."""
import uuid
from datetime import datetime, timezone

from .base import MAX_SCENARIOS_PER_SESSION, ScenarioLimitError, ScenarioNameTaken


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryScenarioStore:
    def __init__(self) -> None:
        self._rows: dict[str, dict[str, dict]] = {}  # session -> id -> row

    @staticmethod
    def _name_taken(rows: dict[str, dict], name: str, except_id: str | None = None) -> bool:
        return any(r["name"] == name and r["id"] != except_id for r in rows.values())

    def list(self, session_id):
        rows = self._rows.get(session_id, {}).values()
        return sorted(rows, key=lambda r: r["updatedAt"], reverse=True)

    def create(self, session_id, name, inputs):
        rows = self._rows.setdefault(session_id, {})
        if len(rows) >= MAX_SCENARIOS_PER_SESSION:
            raise ScenarioLimitError
        if self._name_taken(rows, name):
            raise ScenarioNameTaken
        row = {"id": str(uuid.uuid4()), "name": name, "inputs": inputs, "updatedAt": _now()}
        rows[row["id"]] = row
        return row

    def update(self, session_id, scenario_id, name, inputs):
        rows = self._rows.get(session_id, {})
        row = rows.get(scenario_id)
        if row is None:
            return None
        if self._name_taken(rows, name, except_id=scenario_id):
            raise ScenarioNameTaken
        row.update(name=name, inputs=inputs, updatedAt=_now())
        return row

    def delete(self, session_id, scenario_id):
        return self._rows.get(session_id, {}).pop(scenario_id, None) is not None
