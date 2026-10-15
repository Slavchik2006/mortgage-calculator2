"""HTTP layer: transport, status codes and error shape only. No business logic."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict

from ..core.calculation import calculate
from ..core.types import LoanInput
from ..core.validation import validate
from ..storage.base import ScenarioLimitError, ScenarioNameTaken, ScenarioStore
from .serialization import result_to_dict

router = APIRouter(prefix="/api/v1")

MAX_FIELD_LEN = 32
_NAME_TAKEN = {"error": "A scenario with this name already exists."}


class RawInput(BaseModel):
    """Shape only: every field is a string. Semantic validation lives in core.validation."""

    model_config = ConfigDict(extra="ignore")
    price: str | None = None
    downPayment: str | None = None
    annualRate: str | None = None
    termYears: str | None = None
    annualTax: str | None = None
    annualInsurance: str | None = None


class ScenarioBody(BaseModel):
    name: str
    inputs: RawInput


def _unprocessable(errors: dict[str, str]) -> HTTPException:
    return HTTPException(422, detail={"errors": errors})


def _validated(raw: RawInput) -> LoanInput:
    data = raw.model_dump()
    too_long = {k: "Value is too long." for k, v in data.items() if isinstance(v, str) and len(v) > MAX_FIELD_LEN}
    if too_long:
        raise _unprocessable(too_long)
    result = validate(data)
    if isinstance(result, dict):
        raise _unprocessable(result)
    return result


def get_store(request: Request) -> ScenarioStore:
    return request.app.state.store


def session_id(x_session_id: Annotated[str | None, Header()] = None) -> str:
    """Anonymous session id: a client-generated UUID, treated as an unguessable bearer value."""
    try:
        return str(uuid.UUID(x_session_id or ""))
    except ValueError:
        raise HTTPException(400, detail={"error": "Missing or invalid X-Session-Id header (UUID expected)."}) from None


Store = Annotated[ScenarioStore, Depends(get_store)]
Session = Annotated[str, Depends(session_id)]


def _clean_name(name: str) -> str:
    name = name.strip()
    if not 1 <= len(name) <= 60:
        raise _unprocessable({"name": "Name must be 1-60 characters."})
    return name


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/calculate")
def calculate_endpoint(body: RawInput) -> dict:
    return result_to_dict(calculate(_validated(body)))


@router.get("/scenarios")
def list_scenarios(sid: Session, store: Store) -> list[dict]:
    return store.list(sid)


@router.post("/scenarios", status_code=201)
def create_scenario(body: ScenarioBody, sid: Session, store: Store) -> dict:
    name = _clean_name(body.name)
    _validated(body.inputs)
    try:
        return store.create(sid, name, body.inputs.model_dump())
    except ScenarioLimitError:
        raise HTTPException(409, detail={"error": "Scenario limit reached (50)."}) from None
    except ScenarioNameTaken:
        raise HTTPException(409, detail=_NAME_TAKEN) from None


@router.put("/scenarios/{scenario_id}")
def update_scenario(scenario_id: uuid.UUID, body: ScenarioBody, sid: Session, store: Store) -> dict:
    name = _clean_name(body.name)
    _validated(body.inputs)
    try:
        row = store.update(sid, str(scenario_id), name, body.inputs.model_dump())
    except ScenarioNameTaken:
        raise HTTPException(409, detail=_NAME_TAKEN) from None
    if row is None:
        raise HTTPException(404, detail={"error": "Scenario not found."})
    return row


@router.delete("/scenarios/{scenario_id}", status_code=204)
def delete_scenario(scenario_id: uuid.UUID, sid: Session, store: Store) -> Response:
    if not store.delete(sid, str(scenario_id)):
        raise HTTPException(404, detail={"error": "Scenario not found."})
    return Response(status_code=204)
