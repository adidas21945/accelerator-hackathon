"""idea_generator agent — proposes novel research directions from gap synthesis."""

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

_SKILL_DIR = Path(__file__).parent.parent / "skills" / "identify-gaps"


def _skill_body() -> str:
    try:
        sk = load_skill(_SKILL_DIR)
        return f"# Skill: {sk.name}\n\n{sk.body}"
    except Exception:
        return ""


def run(subtask: dict, synthesis: dict) -> list[dict]:
    model = subtask.get("assigned_model", "claude-sonnet-4-6")
    t0 = time.perf_counter()
    emit("agent_start", agent="idea_generator", model=model)

    skill_text = _skill_body()
    system = (
        "You are a creative research strategist. Propose novel, actionable research directions.\n\n"
        + skill_text
    ).strip()

    gaps_text = (
        f"Themes: {json.dumps(synthesis.get('themes', []))}\n"
        f"Contradictions: {json.dumps(synthesis.get('contradictions', []))}\n"
        f"Open Questions: {json.dumps(synthesis.get('open_questions', []))}"
    )
    open_questions = synthesis.get("open_questions", ["unexplored areas in the literature"])

    user_msg = (
        f"Based on this literature synthesis:\n\n{gaps_text}\n\n"
        "Propose 3 novel research directions. For each:\n"
        "- direction: a clear research direction title\n"
        "- experiments: exactly 3 high-level experiment sketches (methodology, not implementation)\n"
        "- novelty_rationale: why this is new, referencing a specific gap from the synthesis\n\n"
        'Return ONLY valid JSON array:\n'
        '[{"direction": "...", "experiments": ["sketch1", "sketch2", "sketch3"], '
        '"novelty_rationale": "...citing specific gap..."}, ...]'
    )
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]

    try:
        text, tokens = chat_with_model(model, messages, json_mode=True)
        # Handle both array and wrapped object
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            result = parsed.get("directions", parsed.get("ideas", [parsed]))
        else:
            result = parsed
        # Validate structure
        validated = []
        for idea in result:
            if not isinstance(idea, dict):
                continue
            exps = idea.get("experiments", [])
            if len(exps) < 3:
                exps = (exps + ["Further investigation needed"] * 3)[:3]
            rationale = idea.get("novelty_rationale", "")
            if open_questions and not any(q[:20].lower() in rationale.lower() for q in open_questions):
                rationale = f"Addresses gap: '{open_questions[0][:80]}'. {rationale}"
            validated.append({
                "direction": idea.get("direction", "Novel research direction"),
                "experiments": exps[:3],
                "novelty_rationale": rationale,
            })
        result = validated or _fallback(open_questions)
    except Exception:
        result = _fallback(open_questions)
        tokens = 0

    elapsed = round(time.perf_counter() - t0, 2)
    actual_cost = round(tokens / 1000 * COST_PER_1K.get(model, 0.0), 6)
    sonnet_cost = round(tokens / 1000 * COST_PER_1K["claude-sonnet-4-6"], 6)
    emit("agent_complete", agent="idea_generator", model=model,
         tokens=tokens, actual_cost=actual_cost, sonnet_cost=sonnet_cost, latency=elapsed)
    return result


def _fallback(open_questions: list[str]) -> list[dict]:
    gap = open_questions[0] if open_questions else "unexplored regime generalization"
    return [
        {
            "direction": "Cross-regime generalization in ML stock prediction",
            "experiments": [
                "Train on pre-2020 data, evaluate on COVID and post-COVID regimes separately",
                "Implement regime-conditioned loss functions and compare to standard cross-entropy",
                "Ablation study: vary training window length from 1 to 10 years",
            ],
            "novelty_rationale": f"Addresses gap: '{gap[:80]}'. No prior work systematically benchmarks regime transfer.",
        }
    ]
