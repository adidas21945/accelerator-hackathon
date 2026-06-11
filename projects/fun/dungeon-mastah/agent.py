"""dungeon-mastah — the Boston-accented game master agent.

Theater-of-the-mind one-shots with three honest agent lessons inside the
fun: dice come from a TESTED deterministic script (the players can smell
fake dice), session memory is just the message transcript on disk
(AgentResult.messages -> --save / --load / --play), and a strict scene
template keeps a 3B model tight instead of rambling.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Self-locate the repo root: plain `python agent.py` works from anywhere,
# no editable install or cwd assumptions.
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "agentkit").is_dir())))

from agentkit import run_agent, tool  # noqa: E402

DEFAULT_SKILL = HERE / "skills" / "campaign-rules"
DEFAULT_SAVE = HERE / "campaign" / "save.json"

# The dice logic ships inside the skill (scripts/roll.py) so the skill is a
# complete unit; import it here rather than shelling out.
sys.path.insert(0, str(DEFAULT_SKILL / "scripts"))
from roll import roll_spec  # noqa: E402

SYSTEM = (
    "You are Dungeon Mastah, a game mastah from Boston running a tabletop "
    "one-shot — warm, wicked funny, a little dramatic. Check the party sheet "
    "before the first scene. When the players act, call the dice tool first "
    "and narrate second — never decide an uncertain outcome yourself."
)


@tool
def roll_dice(spec: str):
    """Roll dice like 1d20+2. ALWAYS use this for any check, attack, or chance event — never invent roll results."""
    line = roll_spec(spec)
    return f"{line}\nQuote the dice line above word-for-word inside ## Scene, then narrate what it causes."


@tool
def party_sheet():
    """Read the party sheet: each hero's name, class, HP, and gear. Check it before the first scene."""
    pcs = json.loads((HERE / "campaign" / "party.json").read_text())
    return " ".join(f"{p['name']} the {p['class']}: {p['hp']} HP, carries {p['item']}." for p in pcs)


# ── table rules, enforced in code: a 3B keeps the template ~70% of a take,
#    so the dress code is checked deterministically instead of by willpower.
_HEADINGS = ("## Scene", "## Party status", "## Your options")
# One known 3B tic: the genre line "**What do you do?**" lands where the
# "## Your options" heading belongs. Renamed mechanically; content untouched.
_OPTIONS_TIC = re.compile(r"^\s*\*{0,2}what do you (?:do|want to do)\??\*{0,2}:?\s*$", re.I | re.M)


def _sections(text: str) -> dict:
    """Split a reply into {canonical heading: section text}."""
    out, current = {}, None
    for line in text.splitlines():
        hit = next((h for h in _HEADINGS if line.strip().lower().startswith(h.lower())), None)
        current = hit or current
        if current:
            out.setdefault(current, []).append(line)
    return {h: "\n".join(ls).strip() for h, ls in out.items()}

def _missing(text: str) -> list:
    """Headings whose section is absent or empty of its required content."""
    s = _sections(text)
    bad = lambda h, body: (h == "## Party status" and not re.search(r"\d", body)) or (
        h == "## Your options" and len(re.findall(r"^\s*\d+\.", body, re.M)) < 2)
    return [h for h in _HEADINGS if h not in s or bad(h, s[h])]

def _dice_ok(r) -> bool:
    """Every dice line actually rolled is quoted; no roll was faked as text."""
    rolled = [c[2].splitlines()[0] for c in r.tool_calls if c[0] == "roll_dice" and " = " in c[2]]
    return all(line in r.text for line in rolled) and "roll_dice" not in r.text

def _merge(r, r2) -> "AgentResult":
    """One result out of two model calls, with the TRUE total spend."""
    return r2._replace(turns=r.turns + r2.turns, tool_calls=r.tool_calls + r2.tool_calls,
                       usage={k: r.usage[k] + r2.usage[k] for k in r.usage},
                       cost_usd=round(r.cost_usd + r2.cost_usd, 6),
                       latency_s=round(r.latency_s + r2.latency_s, 2))


def _take(task: str, skill, messages=None):
    """One GM take: run, canonicalize the options tic, and if sections are
    missing (3B replies truncate) ask for ONLY those and assemble in code."""
    r = run_agent(task, tools=[roll_dice, party_sheet], skill=skill, system=SYSTEM, messages=messages)
    text = _OPTIONS_TIC.sub("## Your options", r.text, count=1) if "## your options" not in r.text.lower() else r.text
    if missing := _missing(text):
        fill = run_agent(
            "You stopped before finishing the reply. Continue it now: output ONLY the missing "
            "sections, exactly these headings and nothing else: " + ", ".join(missing) +
            ". ## Party status is one line per hero with HP; ## Your options is three numbered "
            "one-sentence options.", tools=(), messages=r.messages)
        have, extra = _sections(text), _sections(fill.text)
        parts = [have.get(h) or extra.get(h, "") for h in _HEADINGS]  # the take's own sections always win
        r = _merge(r, fill._replace(text="\n\n".join(p for p in parts if p)))
    else:
        r = r._replace(text=text)
    return r


def run(task: str, skill=DEFAULT_SKILL, messages=None):
    """The agent contract every project honors: run(task, skill=...) -> AgentResult.

    messages=None is a fresh one-shot (what the evals call); pass a saved
    transcript to continue that session instead. With the skill loaded, the
    reply's format is validated in code: a truncated take gets one fill-in
    turn, a broken take gets ONE fresh retake. Footer numbers include every
    take (the true spend); the raw transcript in .messages is never rewritten.
    """
    if skill is None:
        return run_agent(task, tools=[roll_dice, party_sheet], skill=None, system=SYSTEM,
                         messages=messages)  # the eval baseline stays untouched
    r = _take(task, skill, messages)
    if messages is None and (_missing(r.text) or not _dice_ok(r)):
        r2 = _take(task, skill)  # one fresh retake, then live with the better take
        score = lambda x: len(_missing(x.text)) + (not _dice_ok(x))  # noqa: E731
        best = r2 if score(r2) <= score(r) else r
        r = _merge(r, r2)._replace(text=best.text, messages=best.messages)
    return r


def _footer(r):
    print(
        f"\n[{r.turns} turns · {r.usage['prompt_tokens']}+{r.usage['completion_tokens']} tok"
        f" · ${r.cost_usd} · {r.latency_s}s · tools: {[c[0] for c in r.tool_calls]}]",
        file=sys.stderr,
    )


def main():
    ap = argparse.ArgumentParser(description="Dungeon Mastah — Boston-accented game-master agent")
    ap.add_argument("task", help='e.g. "Start a one-shot adventure in a haunted Boston brownstone."')
    ap.add_argument("--no-skill", action="store_true", help="run without the skill (the eval baseline)")
    ap.add_argument("--offline", action="store_true", help="force fixture mode (this project is offline anyway)")
    ap.add_argument("--save", nargs="?", const=str(DEFAULT_SAVE), default=None, metavar="FILE",
                    help="write the session transcript after the run (default campaign/save.json)")
    ap.add_argument("--load", nargs="?", const=str(DEFAULT_SAVE), default=None, metavar="FILE",
                    help="resume a session saved with --save (default campaign/save.json)")
    ap.add_argument("--play", action="store_true",
                    help="keep playing scene by scene (blank line or Ctrl-D ends the session)")
    args = ap.parse_args()
    if args.offline:
        os.environ["AGENT_OFFLINE"] = "1"
    skill = None if args.no_skill else DEFAULT_SKILL
    messages = json.loads(Path(args.load).read_text()) if args.load else None

    r = run(args.task, skill=skill, messages=messages)
    print(r.text)
    _footer(r)
    while args.play:
        try:
            nxt = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not nxt:
            break
        r = run(nxt, skill=skill, messages=r.messages)  # the transcript IS the session memory
        print(r.text)
        _footer(r)
    if args.save:
        Path(args.save).write_text(json.dumps(r.messages, indent=2), encoding="utf-8")
        print(f"[session saved to {args.save} — resume with --load]", file=sys.stderr)


if __name__ == "__main__":
    main()
