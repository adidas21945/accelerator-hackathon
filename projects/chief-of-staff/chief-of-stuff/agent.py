"""chief-of-stuff — the morning-brief orchestrator (Lane 3 flagship).

One hub, three specialists, two skills. The hub delegates with plain Python
function calls — read run_brief() in agents/orchestrator.py; the whole
mechanism is a screenful — routes each call to the cheapest model that can
do the job, and prints a per-agent routing table after every run.
BriefingClaw's hub-and-spoke architecture at starter scale.

Two commands:
    agent.py "Build my morning brief for Friday, June 26, 2026."
    agent.py --prep "Client sync — Beacon Hill Bikes"     (or task "prep: …")

For evals: skill=None strips the skill from the FINAL render call only — the
specialists still run. The skill template is the thing being measured.
"""

import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Self-locate the repo root: plain `python agent.py` works from anywhere,
# no editable install or cwd assumptions.
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "agentkit").is_dir())))
sys.path.insert(0, str(HERE))  # the agents/ package ships with this project

from agents import orchestrator  # noqa: E402

DEFAULT_SKILL = HERE / "skills" / "morning-brief"
PREP_SKILL = HERE / "skills" / "meeting-prep"


def run(task: str, skill=DEFAULT_SKILL):
    """The agent contract: run(task, skill=...) -> result with .text/.cost_usd.

    Tasks starting with "prep:" route to the meeting-prep path. Any non-None
    skill there means skills/meeting-prep — the eval runner only knows one
    skill dir per project, so the hub translates.
    """
    if task.strip().lower().startswith("prep:"):
        title = task.split(":", 1)[1].strip()
        return orchestrator.run_prep(title, skill=PREP_SKILL if skill is not None else None)
    return orchestrator.run_brief(task, skill=skill)


def main():
    ap = argparse.ArgumentParser(description="chief-of-stuff — morning-brief orchestrator")
    ap.add_argument("task", nargs="?", default="Build my morning brief for today.",
                    help='e.g. "Build my morning brief for Friday, June 26, 2026."')
    ap.add_argument("--prep", metavar="MEETING",
                    help="one-pager for one meeting instead of the full brief")
    ap.add_argument("--no-skill", action="store_true",
                    help="run without the skill (the eval baseline)")
    ap.add_argument("--offline", action="store_true",
                    help="force fixtures + local models only")
    args = ap.parse_args()
    if args.offline:
        os.environ["AGENT_OFFLINE"] = "1"
    task = f"prep: {args.prep}" if args.prep else args.task
    r = run(task, skill=None if args.no_skill else DEFAULT_SKILL)
    print(r.text)
    calls = sum(1 for x in r.routing_table if x["model"] != "(code)")
    print(f"\n[{calls} model calls · {r.usage['prompt_tokens']}+{r.usage['completion_tokens']} tok"
          f" · ${r.cost_usd} · {r.latency_s}s]", file=sys.stderr)
    orchestrator.print_routing_table(r.routing_table)


if __name__ == "__main__":
    main()
