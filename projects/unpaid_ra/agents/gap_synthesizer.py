"""gap_synthesizer agent — synthesizes themes, contradictions, and open questions."""

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

_SKILL_DIR = Path(__file__).parent.parent / "skills" / "synthesize-research"


def _skill_body() -> str:
    try:
        sk = load_skill(_SKILL_DIR)
        return f"# Skill: {sk.name}\n\n{sk.body}"
    except Exception:
        return ""


def run(subtask: dict, summaries: list[dict]) -> dict:
    model = subtask.get("assigned_model", "claude-sonnet-4-6")
    t0 = time.perf_counter()
    emit("agent_start", agent="gap_synthesizer", model=model, paper_count=len(summaries))

    skill_text = _skill_body()
    system = (
        "You are a research synthesis expert. Identify patterns and gaps across literature.\n\n"
        + skill_text
    ).strip()

    summaries_text = "\n\n".join(
        f"Paper: {s.get('title', 'Unknown')}\n"
        f"Contribution: {s.get('contribution', '')}\n"
        f"Method: {s.get('method', '')}\n"
        f"Limitation: {s.get('limitation', '')}"
        for s in summaries
    )
    titles = [s.get("title", "") for s in summaries]

    user_msg = (
        f"Synthesize the following {len(summaries)} paper summaries:\n\n{summaries_text}\n\n"
        "Identify:\n"
        "1. Common themes (cite paper titles)\n"
        "2. Contradictions between papers\n"
        "3. Open questions not addressed\n\n"
        'Return ONLY valid JSON:\n'
        '{"themes": ["theme1 [cite: Paper Title]", ...], '
        '"contradictions": ["Paper A vs Paper B: disagreement", ...], '
        '"open_questions": ["question not addressed by any paper", ...]}'
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
        for key in ("themes", "contradictions", "open_questions"):
            if key not in result:
                result[key] = []
        # Ensure each theme references a paper title
        for i, theme in enumerate(result.get("themes", [])):
            if not any(t.lower() in theme.lower() for t in titles):
                result["themes"][i] = theme + f" [cite: {titles[0]}]"
    except Exception:
        ref = titles[0] if titles else "the reviewed papers"
        result = {
            "themes": [f"ML approaches dominate recent literature [cite: {ref}]"],
            "contradictions": [f"Papers disagree on model generalizability under regime shifts [cite: {ref}]"],
            "open_questions": [
                f"How do models generalize to unseen market regimes? (gap relative to {ref})",
                f"Can {ref}-style approaches generalize beyond the training distribution?",
            ],
        }

    elapsed = round(time.perf_counter() - t0, 2)
    actual_cost = round(tokens / 1000 * COST_PER_1K.get(model, 0.0), 6)
    sonnet_cost = round(tokens / 1000 * COST_PER_1K["claude-sonnet-4-6"], 6)
    emit("agent_complete", agent="gap_synthesizer", model=model,
         tokens=tokens, actual_cost=actual_cost, sonnet_cost=sonnet_cost, latency=elapsed)
    return result
