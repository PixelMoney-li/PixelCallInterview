"""Domain models for the voice call pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CallRequest:
    """A request from the frontend to place an AI voice call."""

    call_id: str
    client_id: str
    destination: str


@dataclass
class CallResult:
    """The artifact a finished call produces, delivered to us via webhook."""

    call_id: str
    destination: str
    summary: str
    transcript: str
    recording_url: str
    # Set by the AI summary when the callee asked not to be called again.
    dnc: bool = False
