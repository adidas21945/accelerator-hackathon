"""researcher — optional relevance pass on the headlines, local tier.

"Is this headline about today's work?" is cheap pattern-matching, not
strategy — and most mornings the right answer is "nothing essential."
An empty section beats confident filler, so this specialist is allowed
to come back empty-handed and the brief says so.
"""

import re

from agentkit import chat

NOTHING = "Nothing essential today."

_SYSTEM = (
    "You filter headlines for a morning brief. Given today's meetings and "
    "todos plus a numbered headline list, answer with AT MOST 3 lines, each:\n"
    "READ <n>: <one clause on why it matters for today's work>\n"
    "If no headline clearly relates to today's work, answer exactly: NONE"
)


def pick_reading(headlines: list[dict], events: list[dict], todos: list[str]):
    """One chat() call -> (reading_bullets, ChatResult | None, route)."""
    if not headlines:
        return NOTHING, None, "skipped (no feed)"
    prompt = (
        "TODAY'S MEETINGS:\n"
        + ("\n".join(f"- {e['title']}" for e in events) or "- (none)")
        + "\n\nTOP TODOS:\n" + "\n".join(f"- {t}" for t in todos[:6])
        + "\n\nHEADLINES:\n"
        + "\n".join(f"{i}. {h['title']}" for i, h in enumerate(headlines, 1))
        + "\n\nWhich headlines (if any) are worth reading today?"
    )
    r = chat(prompt, system=_SYSTEM, provider="local", tier="cheap")
    picks = []
    for m in re.finditer(r"READ\s*#?(\d+)\s*[:.\-—]\s*(.+)", r.text):
        n = int(m[1])
        if 1 <= n <= len(headlines):
            picks.append(f"- {headlines[n - 1]['title']} — {m[2].strip()}")
    return ("\n".join(picks[:3]) if picks else NOTHING), r, "local/cheap"
