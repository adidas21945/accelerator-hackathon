"""skill-forge — the agent that builds skills.

The meta starter: every team at Agent Build Day ships a skill, and this
agent makes the first one a 10-minute job. It interviews you about a job
(or reads an answers.json, or takes a one-line task), drafts a complete
SKILL.md using its own `skill-author` skill, writes it to disk, and PROVES
it by running the agentskills validator — feeding any errors back to the
model for one repair round. The forge is built from the very artifact it
produces.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Self-locate the repo root: plain `python agent.py` works from anywhere,
# no editable install or cwd assumptions.
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "agentkit").is_dir())))

from agentkit import run_agent  # noqa: E402
from agentkit.evals import section  # noqa: E402  (one section parser in the repo)

DEFAULT_SKILL = HERE / "skills" / "skill-author"

SYSTEM = (
    "You are Skill Forge, a skill-writing agent. You turn a job description "
    "into one complete SKILL.md file, ready to validate and install."
)

_FENCE = re.compile(r"```[a-zA-Z]*[ \t]*\n(.*?)\n[ \t]*```", re.S)

NEXT_STEPS = (
    "- Copy the folder into your project's skills/ and pass it to run_agent(skill=...).\n"
    "- Add 3 eval cases and run: uv run python -m agentkit.evals <your-project>.\n"
    "- Re-read the description: it does the routing, so use your tasks' real words."
)


def extract_skill_md(answer: str) -> str | None:
    """Pull the generated SKILL.md out of the model's answer (fenced first)."""
    for block in _FENCE.findall(answer):
        block = block.strip()
        if block.startswith("---") and "name:" in block:
            return block
    m = re.search(r"^---[ \t]*\n.*?\bname:.*?\n---[ \t]*\n.+", answer, re.S | re.M)
    return m.group(0).strip() if m else None  # unfenced fallback for the live demo


def skill_name_of(md: str) -> str | None:
    """Frontmatter `name:` — it decides the directory the skill lands in."""
    parts = md.split("---", 2)
    m = re.search(r"^name:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", parts[1], re.M) if len(parts) > 2 else None
    name = m.group(1).strip() if m else None
    return name if name and "/" not in name and "\\" not in name and ".." not in name else None


def validate_dir(d: Path) -> tuple[bool, str]:
    """Run the agentskills validator (skills_ref CLI, same venv) on a dir."""
    p = subprocess.run(
        [sys.executable, "-m", "skills_ref.cli", "validate", str(d)],
        capture_output=True, text=True, timeout=30,
    )
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def craft_lint(md: str) -> list[str]:
    """The authoring rules the spec validator can't see — code, not willpower."""
    body = md.split("---", 2)[2] if len(md.split("---", 2)) > 2 else ""
    errs = [f"body is missing the {s!r} section"
            for s in ("## Defaults", "## Workflow", "## Gotchas", "## Output template")
            if s.lower() not in body.lower()]
    m = re.search(r"^description:\s*>?-?\s*(.*)$", md, re.M)
    desc = (m.group(1).strip() if m else "")
    if not re.search(r"(?i)\buse\s+when(ever)?\b", md.split("---", 2)[1]):
        errs.append("description must contain 'Use whenever' plus the trigger keywords")
    if 0 < len(desc) < 40:
        errs.append("description is too short to route anything")
    return errs


def _attempt(md: str | None, out_root: Path, old: Path | None) -> tuple[bool, str, Path | None]:
    """Write one draft to <out_root>/<name>/SKILL.md and validate it."""
    if md is None:
        return False, "FAILED: no fenced SKILL.md block found in the answer - nothing to validate.", old
    name = skill_name_of(md)
    if not name:
        return False, "Validation failed: the frontmatter has no parseable name field.", old
    if old and old.name != name:
        shutil.rmtree(old, ignore_errors=True)  # the repair round renamed the skill
    d = out_root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    ok, verdict = validate_dir(d)
    if ok and (errs := craft_lint(md)):
        ok, verdict = False, "Craft check failed (spec frontmatter is fine, but): " + "; ".join(errs)
    return ok, verdict, d


def _section_body(answer: str, name: str) -> str:
    s = section(answer, name)
    return s.split("\n", 1)[1].strip() if "\n" in s else ""


def _compose(answer: str, md: str, verdict: str) -> str:
    """Deterministic four-section report; only the model's prose is reused."""
    name = skill_name_of(md) or "unnamed"
    m = re.search(r"^description:\s*>?-?\s*(.*)$", md, re.M)
    plan = _section_body(answer, "Skill plan") or f"- Name: {name}\n- Purpose: {(m.group(1).strip() if m else '(see description)') or '(see description)'}"
    steps = _section_body(answer, "Next steps") or NEXT_STEPS
    return (
        f"## Skill plan\n{plan}\n\n## SKILL.md\n```markdown\n{md}\n```\n\n"
        f"## Validation\n{verdict}\n\n## Next steps\n{steps}\n"
    )


def forge(task: str, skill=DEFAULT_SKILL, out_dir=None):
    """run_agent -> extract -> write -> validate -> one repair round.

    Returns (AgentResult whose .text is the four-section report, passed, dir).
    """
    out_root = Path(out_dir) if out_dir else Path(tempfile.mkdtemp(prefix="skill-forge-"))
    r = run_agent(task, skill=skill, system=SYSTEM)
    md = extract_skill_md(r.text)
    ok, verdict, sdir = _attempt(md, out_root, None)
    if not ok:  # ONE repair round: the model gets the validator's exact words
        print(f"  -> draft rejected ({verdict.splitlines()[0][:100]}) — repair round", file=sys.stderr)
        fix = run_agent(
            f"The skill validator rejected that answer:\n{verdict}\n"
            "Rewrite the COMPLETE corrected SKILL.md (frontmatter and full body). "
            "Reply with ONLY one fenced ```markdown block.",
            messages=r.messages,
        )
        r = fix._replace(
            turns=r.turns + fix.turns, tool_calls=r.tool_calls + fix.tool_calls,
            usage={k: r.usage.get(k, 0) + fix.usage.get(k, 0) for k in r.usage},
            cost_usd=round(r.cost_usd + fix.cost_usd, 6),
            latency_s=round(r.latency_s + fix.latency_s, 2),
        )
        md = extract_skill_md(fix.text) or md
        ok, verdict, sdir = _attempt(md, out_root, sdir)
    text = _compose(r.text, md, verdict) if md else f"{r.text.rstrip()}\n\n## Validation\n{verdict}"
    return r._replace(text=text), ok, sdir


def run(task: str, skill=DEFAULT_SKILL):
    """The agent contract every project honors: run(task, skill=...) -> AgentResult."""
    return forge(task, skill=skill)[0]


def task_from_answers(a: dict) -> str:
    """Turn an interview (answers dict) into one forge task."""
    bullet = lambda xs: "\n".join(f"- {x}" for x in xs)  # noqa: E731
    lines = [f"Build a skill for this job: {a['job']}"]
    if a.get("name-hint"):
        lines.append(f"Preferred skill name: {a['name-hint']}")
    if a.get("defaults"):
        lines.append("Non-negotiable defaults:\n" + bullet(a["defaults"]))
    if a.get("gotchas"):
        lines.append("Known traps to encode as gotchas:\n" + bullet(a["gotchas"]))
    if a.get("output_sections"):
        lines.append("The skill's output template must require exactly these sections: " + ", ".join(a["output_sections"]))
    if a.get("triggers"):
        lines.append("Trigger keywords for the description: " + ", ".join(a["triggers"]))
    return "\n".join(lines)


def interview() -> dict:
    """The live demo: five questions, one validated skill."""
    print("Skill Forge - answer 5 questions, get a validated skill.\n", file=sys.stderr)
    csv = lambda s: [x.strip() for x in s.split(",") if x.strip()]  # noqa: E731
    return {
        "job": input("1/5 What job should the skill do? "),
        "defaults": csv(input("2/5 Defaults to lock in (comma-separated, blank = forge picks)? ")),
        "gotchas": csv(input("3/5 Traps an expert avoids (comma-separated)? ")),
        "output_sections": csv(input("4/5 Sections every answer must have (comma-separated)? ")),
        "triggers": csv(input("5/5 Trigger keywords for routing (comma-separated)? ")),
    }


def main():
    ap = argparse.ArgumentParser(description="skill-forge — the agent that builds (and validates) skills")
    ap.add_argument("task", nargs="?", help='e.g. "a skill that formats stand-up updates for Slack"')
    ap.add_argument("--answers", help="answers.json instead of the interactive interview")
    ap.add_argument("--out", help="directory to write the skill into (default: a kept tempdir)")
    ap.add_argument("--no-skill", action="store_true", help="run without skill-author (the eval baseline)")
    ap.add_argument("--offline", action="store_true", help="force offline mode (this project is local anyway)")
    args = ap.parse_args()
    if args.offline:
        os.environ["AGENT_OFFLINE"] = "1"
    if args.answers:
        task = task_from_answers(json.loads(Path(args.answers).read_text(encoding="utf-8")))
    else:
        task = args.task or task_from_answers(interview())
    r, ok, sdir = forge(task, skill=None if args.no_skill else DEFAULT_SKILL, out_dir=args.out)
    print(r.text)
    print(
        f"\n[{r.turns} turns · {r.usage['prompt_tokens']}+{r.usage['completion_tokens']} tok"
        f" · ${r.cost_usd} · {r.latency_s}s · skill dir: {sdir if sdir else '—'}]",
        file=sys.stderr,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
