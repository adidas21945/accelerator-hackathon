"""prioritizer — the one judgment call, so it asks for the "strong" tier.

Ranking ten todos against four meetings IS the chief-of-staff job; quality
here is worth paying for. With a frontier key on the machine the call routes
to that provider's strong model; with no key — or offline — it degrades
gracefully to the local model and the routing table says so out loud.
"""

import os
import re

from agentkit import chat

_SYSTEM = (
    "You are a chief of staff picking the top 3 priorities for today. "
    "Output EXACTLY three lines, no preamble, in this shape:\n"
    "1. <action> — <why it must happen today, one clause> (<source file>)\n"
    "2. ...\n3. ...\n"
    "Every line cites ONE source file in parentheses, e.g. (todos.md) or "
    "(2026-06-25-client-sync.md). A hard deadline tied to one of TODAY'S "
    "meetings outranks everything else. Prefer items where a todo, a meeting, "
    "and a note all point at the same thing."
)


def _clip(text: str) -> str:
    """Keep at most the first three numbered lines (a 3B sometimes rambles)."""
    lines = [ln.strip() for ln in text.splitlines() if re.match(r"\s*\d+[.)]", ln)]
    return "\n".join(lines[:3]) if lines else text.strip()


def pick_top3(todos: list[str], events: list[dict], digests: str, date_label: str):
    """One chat() call, strong tier preferred -> (top3_text, ChatResult, route)."""
    prompt = (
        f"Today is {date_label}.\n\nTODAY'S MEETINGS:\n"
        + ("\n".join(f"- {e['time']} {e['title']}" for e in events) or "- (none)")
        + "\n\nOPEN TODOS:\n" + "\n".join(f"- {t}" for t in todos)
        + "\n\nSOURCE DIGESTS:\n" + digests
        + "\n\nPick the top 3 priorities for today."
    )
    if os.getenv("AGENT_OFFLINE"):  # offline = never dial a frontier API
        r = chat(prompt, system=_SYSTEM, provider="local", tier="default")
        return _clip(r.text), r, "strong→local fallback (offline)"
    want = os.getenv("MODEL_PROVIDER", "local")
    want = want if want != "local" else "anthropic"  # the upgrade path: one key
    try:
        r = chat(prompt, system=_SYSTEM, provider=want, tier="strong")
        return _clip(r.text), r, f"{r.provider}/strong"
    except RuntimeError:  # agentkit.resolve: that provider's key is not set
        r = chat(prompt, system=_SYSTEM, provider="local", tier="default")
        return _clip(r.text), r, "strong→local fallback (no key)"
