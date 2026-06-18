"""Mock client for the third-party AI voice call platform."""

from __future__ import annotations

import logging
import threading
import time

from .models import CallRequest

log = logging.getLogger("voice-api")

SLOTS_PER_ACCOUNT = 15


class MockVoiceAPI:
    def __init__(
        self,
        total_slots: int = SLOTS_PER_ACCOUNT,
        dispatch_latency_seconds: float = 0.2,
        call_duration_seconds: float = 30.0,
    ) -> None:
        self._total_slots = total_slots
        self._dispatch_latency_seconds = dispatch_latency_seconds
        self._call_duration_seconds = call_duration_seconds
        self._in_flight = 0
        self._lock = threading.Lock()

    def fetch_call_slot(self) -> int:
        """Return how many voice slots are currently free on the account."""
        with self._lock:
            return self._total_slots - self._in_flight

    def place_call(self, request: CallRequest) -> None:
        with self._lock:
            self._in_flight += 1
        time.sleep(self._dispatch_latency_seconds)  # network round-trip to start the call
        log.info("placed call %s to %s", request.call_id, request.destination)
        # A call holds its slot until it ends; release it when the call finishes.
        threading.Timer(self._call_duration_seconds, self._release_slot).start()

    def _release_slot(self) -> None:
        with self._lock:
            self._in_flight -= 1
