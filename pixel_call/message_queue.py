"""In-memory stand-in for the message queue."""

from __future__ import annotations

import threading
from collections import deque

from .models import CallRequest


class InMemoryMessageQueue:
    def __init__(self) -> None:
        self._items: deque[CallRequest] = deque()
        self._lock = threading.Lock()

    def put(self, request: CallRequest) -> None:
        with self._lock:
            self._items.append(request)

    def poll(self, max_messages: int) -> list[CallRequest]:
        """Return up to max_messages queued requests, removing them from the queue."""
        with self._lock:
            count = min(max_messages, len(self._items))
            return [self._items.popleft() for _ in range(count)]

    def backlog(self) -> int:
        with self._lock:
            return len(self._items)
