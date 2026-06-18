"""Do-Not-Call (DNC) list.

Holds the destinations that asked not to be called again. Written by the webhook handler
when a call's summary is flagged DNC, and read by the Call Service before placing a call.
"""

from __future__ import annotations

import threading


class DncList:
    def __init__(self) -> None:
        self._destinations: set[str] = set()
        self._lock = threading.Lock()

    def add(self, destination: str) -> None:
        with self._lock:
            self._destinations.add(destination)

    def contains(self, destination: str) -> bool:
        with self._lock:
            return destination in self._destinations
