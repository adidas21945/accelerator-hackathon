"""summarizer agent — structures one paper into contribution/method/limitation."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from agentkit.loop import load_skill
from projects.unpaid_ra.events import emit
from projects.unpaid_ra.router.router import COST_PER_1K
from projects.unpaid_ra.agents._util import chat_with_model

_SKILL_DIR = Path(__file__).parent.parent / "skills" / "summarize-paper"


def _skill_body() -> str:
    try:
        sk = load_skill(_SKILL_DIR)
        return f"# Skill: {sk.name}\n\n{sk.body}"
    except Exception:
        return ""


def run(subtask: dict, paper: dict) -> dict:
    model = subtask.get("assigned_model", "claude-haiku-4-5")
    title = paper.get("title", "Unknown")
    t0 = time.perf_counter()
    emit("agent_start", agent="summarizer", model=model, paper_title=title)

    skill_text = _skill_body()
    system = (
        "You are a research assistant. Summarize academic papers into structured format.\n\n"
        + skill_text
    ).strip()

    user_msg = (
        f"Summarize this paper:\n\nTitle: {paper.get('title', '')}\n"
        f"Abstract: {paper.get('abstract', '')}\n\n"
        'Return ONLY valid JSON: {"title": "...", "contribution": "one sentence", '
        '"method": "approach used", "limitation": "key weakness or gap"}'
    )
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]

    tokens = 0
    text = ""
    try:
        text, tokens = chat_with_model(model, messages, json_mode=True)
    except Exception:
        pass

    try:
        result = json.loads(text)
        for key in ("title", "contribution", "method", "limitation"):
            if key not in result:
                result[key] = paper.get(key, "")
    except Exception:
        result = {
            "title": paper.get("title", ""),
            "contribution": paper.get("abstract", "")[:200],
            "method": "See abstract",
            "limitation": "Not extractable",
        }

    elapsed = round(time.perf_counter() - t0, 2)
    actual_cost = round(tokens / 1000 * COST_PER_1K.get(model, 0.0), 6)
    sonnet_cost = round(tokens / 1000 * COST_PER_1K["claude-sonnet-4-6"], 6)
    emit("agent_complete", agent="summarizer", model=model,
         tokens=tokens, actual_cost=actual_cost, sonnet_cost=sonnet_cost, latency=elapsed)
    return result
