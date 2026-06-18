"""Worker: polls the queue on a fixed interval and forwards requests to the voice platform."""

from __future__ import annotations

import logging
import time

from .message_queue import InMemoryMessageQueue
from .voice_api import MockVoiceAPI

log = logging.getLogger("worker")


class Worker:
    def __init__(
        self,
        queue: InMemoryMessageQueue,
        voice_api: MockVoiceAPI,
        poll_interval_seconds: float = 5.0,
    ) -> None:
        self._queue = queue
        self._voice_api = voice_api
        self._poll_interval_seconds = poll_interval_seconds
        self._running = False

    def run(self) -> None:
        self._running = True
        log.info("worker started: polling every %.0fs", self._poll_interval_seconds)
        while self._running:
            available = self._voice_api.fetch_call_slot()
            if available > 0:
                for request in self._queue.poll(available):
                    self._voice_api.place_call(request)
            time.sleep(self._poll_interval_seconds)

    def stop(self) -> None:
        self._running = False
