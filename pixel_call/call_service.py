"""Call Service: accepts call requests and puts them on the queue."""

from __future__ import annotations

import logging

from .dnc import DncList
from .message_queue import InMemoryMessageQueue
from .models import CallRequest

log = logging.getLogger("call-service")


class CallService:
    def __init__(self, queue: InMemoryMessageQueue, dnc_list: DncList) -> None:
        self._queue = queue
        self._dnc_list = dnc_list

    def submit(self, request: CallRequest) -> bool:
        if self._dnc_list.contains(request.destination):
            log.info("blocked call %s: %s is on the DNC list", request.call_id, request.destination)
            return False
        self._queue.put(request)
        return True
