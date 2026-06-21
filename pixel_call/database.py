"""In-memory stand-in for the database (records, summaries, transcripts)."""

from __future__ import annotations

import threading

from .models import CallResult


class InMemoryDB:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.records: dict[str, dict] = {}
        self.summaries: dict[str, str] = {}
        self.transcripts: dict[str, str] = {}

    def save_call_result(self, result: CallResult) -> None:
        with self._lock:
            self.records[result.call_id] = {
                "call_id": result.call_id,
                "destination": result.destination,
                "recording_url": result.recording_url,
                "dnc": result.dnc,
            }
            self.summaries[result.call_id] = result.summary
            self.transcripts[result.call_id] = result.transcript

    def get_call_result(self, call_id: str) -> dict | None:
        with self._lock:
            record = self.records.get(call_id)
            if record is None:
                return None
            return {
                **record,
                "summary": self.summaries.get(call_id),
                "transcript": self.transcripts.get(call_id),
            }
