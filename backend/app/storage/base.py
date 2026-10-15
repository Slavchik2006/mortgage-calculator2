"""Scenario storage interface. Scenarios are scoped by an anonymous session id (no accounts)."""
from typing import Protocol

MAX_SCENARIOS_PER_SESSION = 50


class ScenarioLimitError(Exception):
    pass


class ScenarioNameTaken(Exception):
    pass


class StorageUnavailable(Exception):
    pass


class ScenarioStore(Protocol):
    def list(self, session_id: str) -> list[dict]: ...

    def create(self, session_id: str, name: str, inputs: dict) -> dict:
        """Raises ScenarioLimitError beyond MAX_SCENARIOS_PER_SESSION, ScenarioNameTaken on a duplicate name."""

    def update(self, session_id: str, scenario_id: str, name: str, inputs: dict) -> dict | None:
        """None if the id does not exist in this session. Raises ScenarioNameTaken on a duplicate name."""

    def delete(self, session_id: str, scenario_id: str) -> bool: ...
