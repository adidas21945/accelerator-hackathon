"""CP-Router: single-token logprob confidence probe (Su et al., 2025).

Hits Ollama /api/chat with logprobs to measure complexity confidence,
then assigns the cheapest model that meets the confidence threshold.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from projects.unpaid_ra.events import emit

THRESHOLDS = {"tier1": 0.50, "tier2": 0.65, "tier3": 0.00}
MODELS = {
    "tier1": "granite4:micro",
    "tier2": "claude-haiku-4-5",
    "tier3": "claude-sonnet-4-6",
}
COST_PER_1K = {
    "granite4:micro":    0.000,
    "claude-haiku-4-5":  0.0008,
    "claude-sonnet-4-6": 0.003,
}

_OLLAMA_URL = "http://localhost:11434/api/chat"
_DEFAULT_LOGPROB = -10.0


def _softmax(values: list[float]) -> list[float]:
    m = max(values)
    exps = [math.exp(v - m) for v in values]
    s = sum(exps)
    return [e / s for e in exps]


def _probe(description: str) -> tuple[float, float, float]:
    """Return (p1, p2, p3) confidence that task is tier1/tier2/tier3."""
    prompt = (
        "Rate the complexity of this research subtask as 1 (simple/templated output),\n"
        "2 (moderate reasoning required), or 3 (complex synthesis or open-ended).\n"
        "Reply with only the number.\n\n"
        f"Subtask: {description}\n\n"
        "Complexity:"
    )
    payload = {
        "model": "granite4:micro",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"num_predict": 1},
        "logprobs": True,
        "top_logprobs": 5,
    }
    try:
        resp = httpx.post(_OLLAMA_URL, json=payload, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return _softmax([_DEFAULT_LOGPROB, _DEFAULT_LOGPROB, _DEFAULT_LOGPROB])

    # Extract logprobs from response
    token_logprobs: dict[str, float] = {}
    try:
        # Ollama logprobs are in message.logprobs or choices[0].logprobs
        logprobs_data = (
            data.get("message", {}).get("logprobs")
            or data.get("logprobs")
            or {}
        )
        # Handle both list and dict formats Ollama may return
        if isinstance(logprobs_data, list):
            for entry in logprobs_data:
                if isinstance(entry, dict):
                    tok = entry.get("token", "").strip()
                    lp = entry.get("logprob", _DEFAULT_LOGPROB)
                    if tok in ("1", "2", "3"):
                        token_logprobs[tok] = lp
        elif isinstance(logprobs_data, dict):
            content = logprobs_data.get("content", [])
            if isinstance(content, list):
                for item in content:
                    top = item.get("top_logprobs", [])
                    for entry in top:
                        tok = entry.get("token", "").strip()
                        lp = entry.get("logprob", _DEFAULT_LOGPROB)
                        if tok in ("1", "2", "3"):
                            token_logprobs[tok] = lp
    except Exception:
        pass

    lp1 = token_logprobs.get("1", _DEFAULT_LOGPROB)
    lp2 = token_logprobs.get("2", _DEFAULT_LOGPROB)
    lp3 = token_logprobs.get("3", _DEFAULT_LOGPROB)
    p1, p2, p3 = _softmax([lp1, lp2, lp3])
    return p1, p2, p3


def route(subtask: dict) -> dict:
    """Assign a model tier to a subtask using single-token logprob confidence probe."""
    name = subtask["name"]
    description = subtask.get("description", "")

    emit("probe_start", agent=name, model="granite4:micro", probe_tokens=50)
    p1, p2, p3 = _probe(description)
    emit("probe_result", agent=name,
         confidence_scores={"tier1": round(p1, 3), "tier2": round(p2, 3), "tier3": round(p3, 3)})

    if p1 >= THRESHOLDS["tier1"]:
        tier = "tier1"
    elif p2 >= THRESHOLDS["tier2"]:
        tier = "tier2"
    else:
        tier = "tier3"

    assigned_model = MODELS[tier]
    emit("routing_decision", agent=name,
         tier=tier,
         assigned_model=assigned_model,
         confidence_scores={"tier1": round(p1, 3), "tier2": round(p2, 3), "tier3": round(p3, 3)},
         thresholds=THRESHOLDS,
         signal="logprob_softmax")

    return {
        "subtask": subtask,
        "assigned_model": assigned_model,
        "tier": tier,
        "confidence_scores": {"tier1": p1, "tier2": p2, "tier3": p3},
        "thresholds": THRESHOLDS,
        "signal": "logprob_softmax",
    }
