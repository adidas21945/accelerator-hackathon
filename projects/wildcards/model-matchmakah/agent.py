"""model-matchmakah — the cascade router you can feel.

Every query goes cheap-first: the local 3B answers, grades its own
confidence, and only escalates to a frontier model when it is unsure.
Then the agent shows the receipt — models tried, confidence, dollars,
seconds — rendered by the routing-rationale skill. With no frontier key
it degrades gracefully and says so; the pattern (`agentkit.route.cascade`)
lifts into any other starter and turns the rubric's Model Selection
points into measured numbers.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
# Self-locate the repo root: plain `python agent.py` works from anywhere,
# no editable install or cwd assumptions.
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "agentkit").is_dir())))

from agentkit import llm, route  # noqa: E402
from agentkit.loop import load_skill  # noqa: E402

DEFAULT_SKILL = HERE / "skills" / "routing-rationale"
DEFAULT_THRESHOLD = 0.7
CHEAP = ("local", "default")
STRONG = (None, "strong")  # provider None = $MODEL_PROVIDER → set anthropic|openai|gemini for a real frontier hop
FRONTIER_REF = "claude-sonnet-4-6"  # the "what would frontier-only have cost" yardstick (priced in agentkit.llm)

ANSWER_SYSTEM = "Answer the task directly, correctly, and concisely."
FORMAT_SYSTEM = (
    "You render routing receipts. A skill is loaded — follow its Output template exactly. "
    "Use ONLY the numbers in the routing facts; never invent or change a number."
)

BATCH_TASKS = [
    "What is the capital of Massachusetts?",
    "Explain why switching doors wins the Monty Hall problem, convincingly enough for a skeptic.",
    "A T pass costs $90/month and a single ride costs $2.40. How many rides in a month make the pass the cheaper option? Show the arithmetic.",
    "Write a haiku about the Boston T in winter.",
    "Draft a 3-bullet incident update from these facts: API error rate 14% since 09:12 UTC, cause unknown, payments unaffected, next update by 10:30 UTC.",
]


class MatchResult(NamedTuple):
    text: str          # what the user (and the eval runner) reads
    cost_usd: float    # whole pipeline: cascade + formatting call
    latency_s: float
    route: route.RouteResult
    outcome: str       # one-line routing outcome for the footer


def _strong_unavailable() -> str | None:
    """Why frontier escalation can't happen right now (None = it can)."""
    if os.getenv("AGENT_OFFLINE") == "1":
        return "offline mode (AGENT_OFFLINE=1)"
    try:
        llm.resolve(*STRONG)
        return None
    except RuntimeError as e:  # agentkit names the missing env var in the message
        return f"no frontier key ({str(e).split()[0]} not set)"


def _cascade(task: str, threshold: float):
    """route.cascade with graceful degradation: no key/offline → stay local."""
    reason = _strong_unavailable()
    if reason is None:
        try:
            return route.cascade(task, system=ANSWER_SYSTEM, threshold=threshold,
                                 cheap=CHEAP, strong=STRONG), None
        except RuntimeError as e:  # strong tier died mid-escalation: degrade, stay local
            reason = f"escalation failed ({str(e).splitlines()[0][:60]})"
    # threshold 0.0 can never trip (confidence is clamped to >= 0), so this
    # cascade is guaranteed to answer and grade on the cheap local tier only.
    return route.cascade(task, system=ANSWER_SYSTEM, threshold=0.0,
                         cheap=CHEAP, strong=CHEAP), reason


def _outcome(rr: route.RouteResult, reason: str | None, threshold: float) -> str:
    if rr.escalated:
        final = rr.attempts[-1]
        note = " (the strong tier IS the cheap model — set a frontier key or AGENTKIT_STRONG_MODEL " \
               "for real uplift)" if final.model == rr.attempts[0].model else ""
        return f"escalated to {final.model} — confidence {rr.confidence:.2f} fell below threshold {threshold}{note}"
    if reason and rr.confidence < threshold:
        return f"escalation unavailable — {reason}; staying local"
    return f"resolved locally — confidence {rr.confidence:.2f} met threshold {threshold}"


def _facts(task: str, rr: route.RouteResult, outcome: str, threshold: float) -> str:
    """The raw routing facts the formatter must render — numbers pre-baked."""
    frontier_only = llm.estimate_cost(FRONTIER_REF, rr.attempts[0].usage)
    return "\n".join([
        f"task: {task}",
        f"models tried: {rr.table_row['route']}",
        f"self-confidence: {rr.confidence:.2f} ({'below' if rr.confidence < threshold else 'met'} threshold {threshold})",
        f"escalated: {'yes' if rr.escalated else 'no'}",
        f"est. cost this query: ${rr.total_cost_usd:.4f}",
        f"latency: {rr.table_row['latency_s']} s (includes the self-grading call)",
        f"routing outcome: {outcome}",
        f"frontier-only comparison: the same query sent straight to {FRONTIER_REF} "
        f"would have cost ~${frontier_only:.4f}",
    ])


def run(task: str, skill=DEFAULT_SKILL, threshold: float = DEFAULT_THRESHOLD):
    """The agent contract: run(task, skill=...) -> result with .text.

    skill=None (the eval baseline) returns the cascade's raw answer —
    no receipt, no sections; the formatting call never happens.
    """
    rr, reason = _cascade(task, threshold)
    outcome = _outcome(rr, reason, threshold)
    if skill is None:
        return MatchResult(rr.text, rr.total_cost_usd, rr.table_row["latency_s"], rr, outcome)
    s = load_skill(skill)
    fmt = llm.chat(
        f"# Skill: {s.name}\n\n{s.body}\n\n"
        f"# Raw routing facts\n{_facts(task, rr, outcome, threshold)}\n\n"
        f"# The answer to present\n{rr.text}\n\n"
        "Render the skill's Output template now.",
        system=FORMAT_SYSTEM, provider="local", tier="default",
    )
    return MatchResult(
        fmt.text,
        round(rr.total_cost_usd + fmt.cost_usd, 6),
        round(rr.table_row["latency_s"] + fmt.latency_s, 2),
        rr, outcome,
    )


def batch(threshold: float) -> None:
    """Run the canned task set; print the routing-economics table."""
    print(f"model-matchmakah --batch  (threshold {threshold})\n")
    print(f"{'task':<62} {'route':<34} {'conf':>5} {'cost $':>8} {'sec':>6}")
    print("-" * 119)
    results, reasons = [], set()
    for task in BATCH_TASKS:
        rr, reason = _cascade(task, threshold)
        if reason:
            reasons.add(reason)
        t = rr.table_row
        print(f"{t['task']:<62} {t['route']:<34} {t['confidence']:>5.2f} {t['cost_usd']:>8.4f} {t['latency_s']:>6.1f}")
        results.append(rr)
    print("-" * 119)
    cost = sum(r.total_cost_usd for r in results)
    lat = sum(r.table_row["latency_s"] for r in results)
    local = sum((r.attempts[-1] if r.escalated else r.attempts[0]).provider == "local" for r in results)
    esc = sum(r.escalated for r in results)
    print(f"{'TOTAL':<62} {'':<34} {'':>5} {cost:>8.4f} {lat:>6.1f}")
    print(f"\nresolved locally: {local}/{len(results)} · escalations: {esc}")
    for reason in sorted(reasons):
        print(f"note: escalation unavailable — {reason}; all queries stayed local")


def main():
    ap = argparse.ArgumentParser(description="model-matchmakah — cascade router with receipts")
    ap.add_argument("task", nargs="?", help='e.g. "What is the capital of Massachusetts?"')
    ap.add_argument("--no-skill", action="store_true", help="raw cascade answer, no receipt (the eval baseline)")
    ap.add_argument("--offline", action="store_true", help="never attempt frontier escalation (sets AGENT_OFFLINE=1)")
    ap.add_argument("--batch", action="store_true", help="run the 5 canned tasks; print the routing-economics table")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                    help="escalate below this self-confidence (default 0.7; granite4:micro self-grades "
                         "0.90-1.00, so try 0.3 vs 0.99 to watch the economics flip)")
    args = ap.parse_args()
    if args.offline:
        os.environ["AGENT_OFFLINE"] = "1"
    if args.batch:
        return batch(args.threshold)
    if not args.task:
        ap.error("a task is required (or use --batch)")
    r = run(args.task, skill=None if args.no_skill else DEFAULT_SKILL, threshold=args.threshold)
    print(r.text)
    print(
        f"\n[{r.outcome} · cascade: {r.route.table_row['route']}"
        f" · confidence {r.route.confidence:.2f} · ${r.cost_usd:.4f} · {r.latency_s}s total]",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
