"""orchestrator — the hub. Delegation is plain function calls, on purpose.

run_brief(): ingest (code) → summarizer → prioritizer → researcher → one
final local render through the morning-brief skill. Every model call hands
back an agentkit ChatResult; the hub folds them into a ROUTING TABLE —
model, route, tokens, $, latency per specialist — because "which model did
which job and what did it cost" is the whole Lane-3 argument. The table
prints to stderr after every run and rides on the result as .routing_table.
"""

from __future__ import annotations

import datetime as dt
import re
import sys
import time
from pathlib import Path
from typing import NamedTuple

from agentkit import chat
from agentkit.loop import load_skill

from . import ingest, prioritizer, researcher, summarizer

HERE = Path(__file__).resolve().parent.parent
BRIEFCASE = HERE / "briefcase"
STALE_DAYS = 7

_RENDER_SYSTEM = (
    "You are Chief of Stuff, an executive assistant writing the one page your "
    "boss reads at 7am. Use ONLY the facts provided — never invent meetings, "
    "deadlines, attendees, or sources."
)

_STOP = set("the a an and or of for with to on at in by my our your before about".split())


class BriefResult(NamedTuple):
    text: str
    cost_usd: float
    usage: dict          # {"prompt_tokens": int, "completion_tokens": int}
    latency_s: float
    routing_table: list  # [{agent, model, route, prompt_tokens, ...}, ...]


def _say(msg: str) -> None:
    print(f"  -> {msg}", file=sys.stderr)


def _row(agent: str, r, route: str, latency: float | None = None) -> dict:
    return {
        "agent": agent,
        "model": r.model if r else "(code)",
        "route": route,
        "prompt_tokens": r.usage["prompt_tokens"] if r else 0,
        "completion_tokens": r.usage["completion_tokens"] if r else 0,
        "cost_usd": r.cost_usd if r else 0.0,
        "latency_s": r.latency_s if r else round(latency or 0.0, 2),
    }


def _render(assembly: str, skill):
    """The ONE final call: local model + (optionally) the skill template."""
    system = _RENDER_SYSTEM
    if skill is not None:
        s = skill if hasattr(skill, "body") else load_skill(skill)
        system += f"\n\nA skill is loaded. Follow it exactly.\n\n# Skill: {s.name}\n\n{s.body}"
    return chat(assembly, system=system, provider="local", tier="default")


def _finish(rows: list, text: str, t0: float) -> BriefResult:
    usage = {
        "prompt_tokens": sum(r["prompt_tokens"] for r in rows),
        "completion_tokens": sum(r["completion_tokens"] for r in rows),
    }
    cost = round(sum(r["cost_usd"] for r in rows), 6)
    return BriefResult(text, cost, usage, round(time.perf_counter() - t0, 2), rows)


def run_brief(task: str, skill=None) -> BriefResult:
    t0 = time.perf_counter()
    date = ingest.extract_date(task) or dt.date.today()
    label = date.strftime("%A, %B %d, %Y")

    # 1) ingest — deterministic, $0, and the routing table says so
    events = ingest.parse_calendar(BRIEFCASE / "calendar.ics", date)
    todos = ingest.parse_todos(BRIEFCASE / "todos.md")
    notes = ingest.load_notes(BRIEFCASE / "meeting-notes", today=date)
    heads = ingest.load_headlines(BRIEFCASE / "feeds" / "cached-headlines.xml",
                                  query=" ".join(e["title"] for e in events) or None)
    rows = [_row("ingest", None, "deterministic", time.perf_counter() - t0)]
    _say(f"ingest: {len(events)} events, {len(todos)} todos, {len(notes)} notes, {len(heads)} headlines")

    # 2) the three specialists — explicit delegation, one focused call each
    digests, r1 = summarizer.digest(notes, heads)
    rows.append(_row("summarizer", r1, "local/cheap"))
    _say(f"summarizer done ({r1.latency_s}s)")
    top3, r2, route2 = prioritizer.pick_top3(todos, events, digests, label)
    rows.append(_row("prioritizer", r2, route2))
    _say(f"prioritizer done via {route2} ({r2.latency_s}s)")
    reading, r3, route3 = researcher.pick_reading(heads, events, todos)
    rows.append(_row("researcher", r3, route3))
    _say(f"researcher done ({r3.latency_s if r3 else 0}s)")

    # 3) one final render through the skill template
    stale = [f"{n} ({a} days old)" for n, _, a in notes if a and a > STALE_DAYS]
    sched = "\n".join(
        f"{e['time']} — {e['title']}"
        + (f" (with {', '.join(e['attendees'])})" if e["attendees"] else "")
        for e in events) or "(no meetings on the calendar)"
    assembly = (
        f"DATE: {label}\n\n"
        f"SCHEDULE (calendar.ics — ground truth, already filtered to this date; "
        f"every line below belongs in the brief):\n{sched}\n\n"
        f"TOP 3 PRIORITIES (already ranked — keep order and citations):\n{top3}\n\n"
        f"SOURCE DIGESTS (for meeting-prep pointers):\n{digests}\n\n"
        f"READING CANDIDATES (already filtered for relevance):\n{reading}\n\n"
        f"REMAINING OPEN TODOS:\n" + "\n".join(f"- {t}" for t in todos)
        + f"\n\nSTALE NOTES (flag, never trust silently): {'; '.join(stale) or 'none'}\n\n"
        f"Write the morning brief for {label}."
    )
    r4 = _render(assembly, skill)
    rows.append(_row("render", r4, f"{r4.provider}/default" + ("" if skill else " (no skill)")))
    return _finish(rows, r4.text.strip(), t0)


def _kw(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower())
            if w not in _STOP and len(w) > 2}


def run_prep(title: str, skill=None) -> BriefResult:
    """The composition path: a one-pager for ONE meeting (skills/meeting-prep)."""
    t0 = time.perf_counter()
    events = ingest.parse_calendar(BRIEFCASE / "calendar.ics")
    todos = ingest.parse_todos(BRIEFCASE / "todos.md")
    notes = ingest.load_notes(BRIEFCASE / "meeting-notes")
    kw = _kw(title)
    event = max(events, key=lambda e: len(kw & _kw(e["title"])), default=None)
    if event and not (kw & _kw(event["title"])):
        event = None  # nothing actually matched — don't invent a time
    best = sorted(notes, key=lambda n: len(kw & _kw(n[0] + " " + n[1])), reverse=True)[:2]
    related = [t for t in todos if kw & _kw(t)]
    rows = [_row("ingest", None, "deterministic", time.perf_counter() - t0)]
    when = (f"{event['date']} at {event['time']}"
            + (f", with {', '.join(event['attendees'])}" if event["attendees"] else "")
            ) if event else "NOT on the calendar — say so; do not invent a time"
    _say(f"ingest: matched event: {event['title'] if event else 'none'}; notes: "
         + ", ".join(n[0] for n in best))
    assembly = (
        f"MEETING: {title}\nCALENDAR ENTRY: {when}\n\n"
        + "\n\n".join(f"NOTE {name}:\n{text.strip()[:2000]}" for name, text, _ in best)
        + "\n\nRELATED TODOS:\n"
        + ("\n".join(f"- {t}" for t in related) or "- (none)")
        + "\n\nWrite the prep one-pager for this meeting."
    )
    r = _render(assembly, skill)
    rows.append(_row("render", r, f"{r.provider}/default" + ("" if skill else " (no skill)")))
    return _finish(rows, r.text.strip(), t0)


def print_routing_table(rows: list, file=sys.stderr) -> None:
    """The Lane-3 money shot: who did what, on which model, for how much."""
    fmt = "{:<11} {:<15} {:<33} {:>11} {:>9} {:>6}"
    line = fmt.format("agent", "model", "route", "tok (p+c)", "$", "s")
    print("\n" + "-" * len(line), file=file)
    print(line, file=file)
    for r in rows:
        print(fmt.format(r["agent"], r["model"], r["route"],
                         f"{r['prompt_tokens']}+{r['completion_tokens']}",
                         f"{r['cost_usd']:.4f}", f"{r['latency_s']:.1f}"), file=file)
    print(fmt.format(
        "TOTAL", "", "",
        f"{sum(r['prompt_tokens'] for r in rows)}+{sum(r['completion_tokens'] for r in rows)}",
        f"{sum(r['cost_usd'] for r in rows):.4f}",
        f"{sum(r['latency_s'] for r in rows):.1f}"), file=file)
