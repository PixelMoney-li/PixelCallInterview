"""Webhook handler: stores the finished call's artifacts and updates the DNC list."""

from __future__ import annotations

from .database import InMemoryDB
from .dnc import DncList
from .models import CallResult


class WebhookHandler:
    def __init__(self, db: InMemoryDB, dnc_list: DncList) -> None:
        self._db = db
        self._dnc_list = dnc_list

    def handle(self, result: CallResult) -> None:
        self._db.save_call_result(result)
        if result.dnc:
            self._dnc_list.add(result.destination)
