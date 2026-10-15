"""In-memory store: default for development and tests."""
import uuid
from datetime import datetime, timezone

from .base import MAX_SCENARIOS_PER_SESSION, ScenarioLimitError


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryScenarioStore:
    def __init__(self) -> None:
        self._rows: dict[str, dict[str, dict]] = {}  # session -> id -> row

    def list(self, session_id):
        rows = self._rows.get(session_id, {}).values()
        return sorted(rows, key=lambda r: r["updatedAt"], reverse=True)

    def create(self, session_id, name, inputs):
        rows = self._rows.setdefault(session_id, {})
        if len(rows) >= MAX_SCENARIOS_PER_SESSION:
            raise ScenarioLimitError
        row = {"id": str(uuid.uuid4()), "name": name, "inputs": inputs, "updatedAt": _now()}
        rows[row["id"]] = row
        return row

    def update(self, session_id, scenario_id, name, inputs):
        row = self._rows.get(session_id, {}).get(scenario_id)
        if row is None:
            return None
        row.update(name=name, inputs=inputs, updatedAt=_now())
        return row

    def delete(self, session_id, scenario_id):
        return self._rows.get(session_id, {}).pop(scenario_id, None) is not None
