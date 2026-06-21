"""HTTP controller exposing the public call API.

POST /api/call         — place a call request.
GET  /api/call_result  — fetch a finished call's summary / transcript / recording.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .call_service import CallService
from .database import InMemoryDB
from .models import CallRequest

log = logging.getLogger("controller")


class CallCreate(BaseModel):
    client_id: str
    destination: str


class Controller:
    """Wires the HTTP endpoints to the Call Service (writes) and the DB (reads)."""

    def __init__(self, call_service: CallService, db: InMemoryDB) -> None:
        self._call_service = call_service
        self._db = db

    def create_call(self, client_id: str, destination: str) -> tuple[bool, str]:
        call_id = str(uuid.uuid4())
        accepted = self._call_service.submit(CallRequest(call_id, client_id, destination))
        return accepted, call_id

    def get_call_result(self, call_id: str) -> dict | None:
        return self._db.get_call_result(call_id)


def create_app(controller: Controller) -> FastAPI:
    app = FastAPI(title="Pixel Voice Call API")

    @app.post("/api/call", status_code=202)
    def post_call(body: CallCreate) -> dict:
        accepted, call_id = controller.create_call(body.client_id, body.destination)
        if not accepted:
            raise HTTPException(status_code=403, detail="destination on DNC list")
        return {"call_id": call_id}

    @app.get("/api/call_result")
    def get_call_result(call_id: str) -> dict:
        result = controller.get_call_result(call_id)
        if result is None:
            raise HTTPException(status_code=404, detail="call result not found")
        return result

    return app
