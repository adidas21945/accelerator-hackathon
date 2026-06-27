"""Structured event emitter — appends JSON lines to trace.jsonl."""

from __future__ import annotations

import json
import time
from pathlib import Path

_TRACE = Path(__file__).parent / "trace.jsonl"

VALID_TYPES = {
    "agent_start", "agent_complete", "probe_start", "probe_result",
    "routing_decision", "fetch_attempt", "papers_retrieved",
    "wave_start", "wave_complete",
    # allow misc events during development
}


def emit(event_type: str, **kwargs) -> None:
    record = {"type": event_type, "ts": time.time(), **kwargs}
    with _TRACE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
