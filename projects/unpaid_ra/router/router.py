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

THRESHOLDS = {"tier1": 0.50, "tier2": 0.10, "tier3": 0.00}
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


def _probe(description: str, *, debug: bool = False) -> tuple[float, float, float]:
    """Return (p1, p2, p3) confidence that task is tier1/tier2/tier3."""
    # Decision-tree probe: asks two yes/no questions to anchor tier assignment.
    # Grounding in explicit yes/no logic helps granite4:micro reach tier1 for
    # query-generation tasks and tier2 for single-paper summarization.
    prompt = (
        "Answer with a single digit: 1, 2, or 3.\n\n"
        "Rules:\n"
        "- If the task generates search queries or a keyword list → 1\n"
        "- If the task reads and summarizes a single paper → 2\n"
        "- If the task compares papers, finds contradictions, or proposes ideas → 3\n\n"
        f"Task: {description}\n\n"
        "Answer:"
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

    # Ollama native /api/chat returns logprobs as a top-level list:
    # [{"token": "2", "logprob": -0.01, "top_logprobs": [{"token":"2",...}, {"token":"1",...}]}]
    token_logprobs: dict[str, float] = {}
    try:
        logprobs_data = (
            data.get("message", {}).get("logprobs")
            or data.get("logprobs")
            or []
        )
        if isinstance(logprobs_data, list):
            for entry in logprobs_data:
                if not isinstance(entry, dict):
                    continue
                # The generated token itself
                tok = entry.get("token", "").strip()
                lp = entry.get("logprob", _DEFAULT_LOGPROB)
                if tok in ("1", "2", "3"):
                    token_logprobs[tok] = lp
                # All alternatives in top_logprobs
                for alt in entry.get("top_logprobs", []):
                    tok = alt.get("token", "").strip()
                    lp = alt.get("logprob", _DEFAULT_LOGPROB)
                    if tok in ("1", "2", "3"):
                        token_logprobs.setdefault(tok, lp)
        elif isinstance(logprobs_data, dict):
            for item in logprobs_data.get("content", []):
                for alt in item.get("top_logprobs", []):
                    tok = alt.get("token", "").strip()
                    lp = alt.get("logprob", _DEFAULT_LOGPROB)
                    if tok in ("1", "2", "3"):
                        token_logprobs.setdefault(tok, lp)
    except Exception:
        pass

    if debug:
        raw_tokens = [
            f"{e.get('token','?')}={e.get('logprob',0):.3f}"
            for e in (logprobs_data if isinstance(logprobs_data, list) else [])
        ]
        print(f"  [router debug] raw top token(s): {raw_tokens}")
        print(f"  [router debug] found 1/2/3 logprobs: {token_logprobs}")

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
