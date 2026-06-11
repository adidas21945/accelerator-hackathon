"""fridge-whisperer — the what's-for-dinner agent.

The gentlest starter in the repo: two zero-argument tools, one skill, no
network, runs entirely on a local model. The agent reads your pantry and
diet notes through tools, then the skill turns "stuff I have" into a plan
and a grocery list a real household can shop from.
"""

import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Self-locate the repo root: plain `python agent.py` works from anywhere,
# no editable install or cwd assumptions.
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "agentkit").is_dir())))

from agentkit import run_agent, tool  # noqa: E402

DEFAULT_SKILL = HERE / "skills" / "meal-plan"

SYSTEM = (
    "You are Fridge Whisperer, a practical meal-planning agent. "
    "Always read the pantry staples and the diet notes with your tools "
    "before you plan anything."
)


@tool
def read_pantry_staples():
    """List the staples already in the pantry. Always check this before writing a grocery list."""
    return (HERE / "pantry" / "staples.txt").read_text()


@tool
def read_diet_notes():
    """Read the household's diet notes (allergies, hard rules). Always check this before planning meals."""
    return (HERE / "pantry" / "diet.txt").read_text()


def run(task: str, skill=DEFAULT_SKILL):
    """The agent contract every project honors: run(task, skill=...) -> AgentResult."""
    return run_agent(
        task,
        tools=[read_pantry_staples, read_diet_notes],
        skill=skill,
        system=SYSTEM,
    )


def main():
    ap = argparse.ArgumentParser(description="Fridge Whisperer — meal-plan agent")
    ap.add_argument("task", help='e.g. "I have chicken thighs, broccoli, and rice. Plan 3 dinners for 2."')
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
