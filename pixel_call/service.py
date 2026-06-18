"""Container entrypoint for the deployable tiers of the voice call pipeline.

The pipeline runs as three independently deployable processes — the Call Service, the
Worker, and the Webhook Handler (see docker-compose.yml). This module starts whichever
tier the container is launched as.
"""

from __future__ import annotations

import argparse
import logging
import os
import time

from .call_service import CallService
from .database import InMemoryDB
from .dnc import DncList
from .message_queue import InMemoryMessageQueue
from .voice_api import MockVoiceAPI
from .webhook import WebhookHandler
from .worker import Worker

ROLES = ("call-service", "worker", "webhook")

log = logging.getLogger("service")


def run_call_service() -> None:
    queue = InMemoryMessageQueue()
    dnc_list = DncList()
    service = CallService(queue, dnc_list)
    log.info("Call Service up: accepting call requests and enqueueing them (skipping DNC numbers)")
    # In production an HTTP endpoint would call service.submit(request) per inbound request.
    _serve_forever(service)


def run_worker() -> None:
    queue = InMemoryMessageQueue()
    voice_api = MockVoiceAPI()
    poll_interval = float(os.getenv("POLL_INTERVAL_SECONDS", "5"))
    Worker(queue, voice_api, poll_interval).run()


def run_webhook() -> None:
    db = InMemoryDB()
    dnc_list = DncList()
    handler = WebhookHandler(db, dnc_list)
    log.info("Webhook Handler up: storing summaries/transcripts/recordings and updating the DNC list")
    # In production an HTTP endpoint would call handler.handle(result) per webhook POST.
    _serve_forever(handler)


def _serve_forever(_component: object) -> None:
    while True:
        time.sleep(60)


_RUNNERS = {
    "call-service": run_call_service,
    "worker": run_worker,
    "webhook": run_webhook,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one tier of the voice call pipeline.")
    parser.add_argument("role", choices=ROLES, help="which tier this container runs")
    role = parser.parse_args().role

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    _RUNNERS[role]()


if __name__ == "__main__":
    main()
