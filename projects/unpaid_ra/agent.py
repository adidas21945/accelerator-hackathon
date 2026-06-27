"""UnpaidRA — give it a research field, get back what took your RA three weeks."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = next(p for p in HERE.parents if (p / "agentkit").is_dir())
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(HERE))

_TRACE = HERE / "trace.jsonl"
_DEMO_TRACE = HERE / "fixtures" / "demo_trace.jsonl"
_COST_PER_1K = {
    "granite4:micro":    0.000,
    "claude-haiku-4-5":  0.0008,
    "claude-sonnet-4-6": 0.003,
    "mcp/fetch_papers":  0.000,
}


def _clear_trace() -> None:
    _TRACE.write_text("", encoding="utf-8")


def _read_trace() -> list[dict]:
    if not _TRACE.exists():
        return []
    lines = []
    for line in _TRACE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                lines.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return lines


def _compute_summary(result: dict, events: list[dict]) -> dict:
    """Compute token/cost summary from trace events."""
    total_tokens = 0
    total_cost = 0.0
    sonnet_cost = 0.0
    model_counts: dict[str, int] = {}

    for ev in events:
        if ev.get("type") == "agent_complete":
            model = ev.get("model", "")
            toks = ev.get("tokens", 0) or 0
            cost = ev.get("actual_cost", 0.0) or 0.0
            s_cost = ev.get("sonnet_cost", 0.0) or 0.0
            total_tokens += toks
            total_cost += cost
            sonnet_cost += s_cost
            if model and model != "mcp/fetch_papers":
                model_counts[model] = model_counts.get(model, 0) + 1

    savings_pct = 0.0
    if sonnet_cost > 0:
        savings_pct = round((sonnet_cost - total_cost) / sonnet_cost * 100, 1)

    routing_parts = [f"{m} ×{c}" for m, c in sorted(model_counts.items())]

    return {
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 6),
        "sonnet_baseline": round(sonnet_cost, 6),
        "savings_pct": savings_pct,
        "routing": "  ".join(routing_parts) if routing_parts else "local only",
        "idea_count": len(result.get("ideas", [])),
    }


def _print_summary(field: str, summary: dict) -> None:
    print("\nUnpaidRA — run complete")
    print("─" * 53)
    print(f"Field:      {field}")
    print(f"Waves:      5 completed")
    agents_count = 5 + 1 + 1  # 5 summarizers + gap synthesizer + idea generator
    print(f"Agents:     {agents_count} calls (5 summarizers + gap synthesizer + idea generator)")
    print(f"Routing:    {summary['routing']}")
    print(f"Tokens:     {summary['total_tokens']}")
    print(f"Cost:       ${summary['total_cost']} actual  vs  ${summary['sonnet_baseline']} all-Sonnet baseline")
    print(f"Savings:    {summary['savings_pct']}% cost reduction")
    print("─" * 53)
    print(f"Ideas generated: {summary['idea_count']}")
    print("Evals:      run `uv run python projects/unpaid-ra/evals/run_evals.py` to score")


def _replay_mode() -> None:
    """Tail demo_trace.jsonl at 50ms per event."""
    if not _DEMO_TRACE.exists():
        # Fall back to the current trace
        src = _TRACE
    else:
        src = _DEMO_TRACE
    events = []
    if src.exists():
        for line in src.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    for ev in events:
        print(json.dumps(ev))
        time.sleep(0.05)


def main() -> None:
    ap = argparse.ArgumentParser(description="UnpaidRA — multi-agent research system")
    ap.add_argument("field", nargs="?", default="ML models for stock return prediction")
    ap.add_argument("--offline", action="store_true", help="Force fixture fallback")
    ap.add_argument("--replay", action="store_true", help="Replay demo trace at 50ms/event")
    args = ap.parse_args()

    if args.replay:
        _replay_mode()
        return

    if args.offline:
        os.environ["AGENT_OFFLINE"] = "1"

    _clear_trace()

    from projects.unpaid_ra.planner.planner import plan
    from projects.unpaid_ra import dispatcher

    subtasks = plan(args.field)
    result = asyncio.run(dispatcher.run(args.field, subtasks))

    # Save final output alongside trace
    output_path = HERE / "fixtures" / "last_run.json"
    output_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    events = _read_trace()
    summary = _compute_summary(result, events)
    _print_summary(args.field, summary)


if __name__ == "__main__":
    main()
