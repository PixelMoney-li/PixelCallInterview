"""Mock client for the third-party AI voice call platform."""

from __future__ import annotations

import logging
import threading
import time

from .models import CallRequest, CallResult

log = logging.getLogger("voice-api")

SLOTS_PER_ACCOUNT = 100


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
        self._results: dict[str, CallResult] = {}  # the provider's own copy of each finished call
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
        # When the call ends, the provider produces the artifacts and frees the slot.
        threading.Timer(self._call_duration_seconds, self._complete_call, args=(request,)).start()

    def fetch_call_result(self, call_id: str) -> CallResult | None:
        """Read back the artifacts the provider stored for a finished call."""
        with self._lock:
            return self._results.get(call_id)

    def _complete_call(self, request: CallRequest) -> None:
        result = CallResult(
            call_id=request.call_id,
            destination=request.destination,
            summary=f"AI summary for call {request.call_id} to {request.destination}",
            transcript=f"Transcript for call {request.call_id}",
            recording_url=f"https://recordings.voice-provider.example/{request.call_id}.mp3",
        )
        with self._lock:
            self._results[request.call_id] = result
            self._in_flight -= 1
        log.info("call %s finished; artifacts stored by provider", request.call_id)
