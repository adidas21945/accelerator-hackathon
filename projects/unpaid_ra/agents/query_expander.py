"""query_expander agent — generates academic search queries for a research field."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from projects.unpaid_ra.events import emit
from projects.unpaid_ra.router.router import COST_PER_1K
from projects.unpaid_ra.agents._util import chat_with_model

_SYSTEM = "You are a research query specialist. Generate precise academic search queries."

_PROMPT_TMPL = (
    "Generate 3-5 precise, diverse academic search queries for the research field: '{field}'.\n"
    "Each query should target different aspects: methods, applications, benchmarks, recent advances.\n"
    'Return ONLY valid JSON: {{"queries": ["query1", "query2", "query3", "query4", "query5"]}}'
)

_FALLBACK = {
    "queries": [
        "machine learning stock return prediction deep learning",
        "equity return forecasting neural networks",
        "transformer models financial time series prediction",
        "alternative data stock market prediction ML",
        "reinforcement learning portfolio optimization equities",
    ]
}


def run(subtask: dict) -> dict:
    model = subtask.get("assigned_model", "granite4:micro")
    field = subtask.get("input", {}).get("field", "ML models for stock return prediction")
    t0 = time.perf_counter()
    emit("agent_start", agent="query_expander", model=model, field=field)

    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": _PROMPT_TMPL.format(field=field)},
    ]
    try:
        text, tokens = chat_with_model(model, messages, json_mode=True)
        result = json.loads(text)
        if "queries" not in result:
            result = _FALLBACK
    except Exception:
        result = _FALLBACK
        tokens = 0

    elapsed = round(time.perf_counter() - t0, 2)
    actual_cost = round(tokens / 1000 * COST_PER_1K.get(model, 0.0), 6)
    sonnet_cost = round(tokens / 1000 * COST_PER_1K["claude-sonnet-4-6"], 6)
    emit("agent_complete", agent="query_expander", model=model,
         tokens=tokens, actual_cost=actual_cost, sonnet_cost=sonnet_cost, latency=elapsed)
    return result
