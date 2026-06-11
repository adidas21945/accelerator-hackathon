"""ingest — the specialist that is NOT a model: deterministic loaders.

Parsing a calendar, a todo list, notes, and a feed must come out the same
every run, so it is code, not a prompt. The model-backed specialists only
ever see the clean, sentence-shaped facts produced here. That split —
ingestion is code, judgment is models — is the first routing decision.
"""

from __future__ import annotations

import datetime as dt
import os
import re
from pathlib import Path

import feedparser
import requests
from icalendar import Calendar

_MONTHS = {m: i + 1 for i, m in enumerate(
    "january february march april may june july august september october november december".split())}


def extract_date(task: str) -> dt.date | None:
    """Pull an explicit date out of a task string (ISO or 'June 26, 2026')."""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", task)
    if m:
        return dt.date(int(m[1]), int(m[2]), int(m[3]))
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", task)
    if m and m[1].lower() in _MONTHS:
        return dt.date(int(m[3]), _MONTHS[m[1].lower()], int(m[2]))
    return None


def parse_calendar(path: Path, target: dt.date | None = None) -> list[dict]:
    """VEVENTs as {date, time, title, attendees}; `target` filters to one day."""
    cal = Calendar.from_ical(Path(path).read_text(encoding="utf-8"))
    events = []
    for comp in cal.walk("VEVENT"):
        start = comp.decoded("DTSTART")
        date = start.date() if isinstance(start, dt.datetime) else start
        if target and date != target:
            continue
        att = comp.get("ATTENDEE", [])
        att = att if isinstance(att, list) else [att]
        names = [str(a.params.get("CN", "")) for a in att if getattr(a, "params", None)]
        events.append({
            "date": date,
            "time": start.strftime("%H:%M") if isinstance(start, dt.datetime) else "all-day",
            "title": str(comp.get("SUMMARY", "")),
            "attendees": [n for n in names if n],
        })
    return sorted(events, key=lambda e: (str(e["date"]), e["time"]))


def parse_todos(path: Path) -> list[str]:
    """Open '- [ ]' items as sentences, each with a file:line receipt."""
    items = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        m = re.match(r"\s*[-*]\s*\[ \]\s*(.+)", line)
        if m:
            items.append(f"{m[1].strip()} ({Path(path).name}:{n})")
    return items


def load_notes(notes_dir: Path, today: dt.date | None = None) -> list[tuple]:
    """[(filename, text, age_days|None)] — age from the YYYY-MM-DD name prefix."""
    out = []
    for f in sorted(Path(notes_dir).glob("*.md")):
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", f.name)
        age = (today - dt.date(int(m[1]), int(m[2]), int(m[3]))).days if (m and today) else None
        out.append((f.name, f.read_text(encoding="utf-8"), age))
    return out


def load_headlines(feed_xml: Path, query: str | None = None, limit: int = 10) -> list[dict]:
    """Headlines as {title, summary}. With TAVILY_API_KEY set and not offline,
    search Tavily live; on ANY live failure (or no key) fall back to the cached
    RSS fixture — live calls are for demos, fixtures are for measurement."""
    key = os.getenv("TAVILY_API_KEY")
    if key and not os.getenv("AGENT_OFFLINE"):
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": key, "max_results": limit,
                      "query": query or "e-bike fleet and AI agent-skills news"},
                timeout=15)
            resp.raise_for_status()
            live = [{"title": r.get("title", ""), "summary": r.get("content", "")[:200]}
                    for r in resp.json().get("results", [])]
            if live:
                return live[:limit]
        except Exception:
            pass  # the fixture below is the contract; live is a bonus
    feed = feedparser.parse(str(feed_xml))
    return [{"title": e.get("title", ""), "summary": e.get("summary", "")[:200]}
            for e in feed.entries][:limit]
