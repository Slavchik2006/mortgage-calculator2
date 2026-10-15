"""FastAPI app. Run from backend/: uvicorn app.main:app --reload"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .api.routes import router
from .config import build_store
from .storage.base import ScenarioStore, StorageUnavailable


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


def create_app(store: ScenarioStore | None = None) -> FastAPI:
    app = FastAPI(title="mortgage-calculator2 API", version="2.0.0")
    app.state.store = store or build_store()
    app.include_router(router)

    @app.exception_handler(HTTPException)
    async def http_error(_: Request, exc: HTTPException) -> JSONResponse:
        body = exc.detail if isinstance(exc.detail, dict) else {"error": str(exc.detail)}
        return JSONResponse(body, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def bad_request(_: Request, __: RequestValidationError) -> JSONResponse:
        return JSONResponse({"error": "Malformed request body."}, status_code=400)

    @app.exception_handler(StorageUnavailable)
    async def storage_down(_: Request, __: StorageUnavailable) -> JSONResponse:
        return JSONResponse({"error": "Storage unavailable."}, status_code=503)

    # Same-origin frontend, mounted last so /api/* wins
    if FRONTEND_DIR.is_dir():
        app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    return app


app = create_app()
