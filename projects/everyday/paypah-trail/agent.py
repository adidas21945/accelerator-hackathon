"""paypah-trail — the receipts-to-ledger agent (Boston accent included).

Drop receipts in receipts/, ask for a monthly summary. A deterministic,
self-tested script does ALL the byte-level parsing — vendor, date, the
subtotal-vs-total trap — because LLMs must never grope through receipt
formats; the local 3B only categorizes and assembles the report. Privacy
is the pitch: your finances never leave the laptop.
"""

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Self-locate the repo root: plain `python agent.py` works from anywhere,
# no editable install or cwd assumptions.
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "agentkit").is_dir())))

from agentkit import run_agent, tool  # noqa: E402

DEFAULT_SKILL = HERE / "skills" / "expense-report"
RECEIPTS = HERE / "receipts"

# The parser ships INSIDE the skill (scripts do the deterministic work);
# the tool imports it so CLI, selftest, and agent share one tested code path.
_spec = importlib.util.spec_from_file_location(
    "parse_receipt", DEFAULT_SKILL / "scripts" / "parse_receipt.py")
_parser = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_parser)

SYSTEM = (
    "You are Paypah Trail, a local-first expense-report agent. "
    "Always list the receipt files and parse every single one with your "
    "tools before summarizing; never invent vendors, dates, or amounts."
)


@tool
def list_receipts():
    """List the receipt files in the receipts folder with their sizes. Always call this first."""
    files = sorted(p for p in RECEIPTS.iterdir() if p.suffix.lower() in (".txt", ".pdf"))
    if not files:
        return "The receipts folder is empty."
    names = ", ".join(f"{p.name} ({p.stat().st_size} bytes)" for p in files)
    return f"There are {len(files)} receipt files: {names}."


@tool
def parse_receipt(filename: str):
    """Parse one receipt file into JSON (vendor, date, total, category_hint). Call this once per filename from list_receipts; never read receipt text yourself."""
    path = RECEIPTS / Path(filename).name
    if not path.exists():
        return f"No receipt named {filename!r} — call list_receipts for the real filenames."
    return f"Parsed {path.name}: {json.dumps(_parser.parse_file(path))}"


def run(task: str, skill=DEFAULT_SKILL):
    """The agent contract every project honors: run(task, skill=...) -> AgentResult."""
    return run_agent(
        task,
        tools=[list_receipts, parse_receipt],
        skill=skill,
        system=SYSTEM,
        max_turns=12,  # six receipts -> up to six parse turns on a one-call-per-turn 3B
    )


def main():
    ap = argparse.ArgumentParser(description="Paypah Trail — receipts-to-ledger agent")
    ap.add_argument("task", help='e.g. "Summarize my receipts for May 2026."')
    ap.add_argument("--no-skill", action="store_true", help="run without the skill (the eval baseline)")
    ap.add_argument("--offline", action="store_true", help="force fixture mode (this project is offline anyway)")
    args = ap.parse_args()
    if args.offline:
        os.environ["AGENT_OFFLINE"] = "1"
    r = run(args.task, skill=None if args.no_skill else DEFAULT_SKILL)
    print(r.text)
    print(
        f"\n[{r.turns} turns · {r.usage['prompt_tokens']}+{r.usage['completion_tokens']} tok"
        f" · ${r.cost_usd} · {r.latency_s}s · tools: {[c[0] for c in r.tool_calls]}]",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
