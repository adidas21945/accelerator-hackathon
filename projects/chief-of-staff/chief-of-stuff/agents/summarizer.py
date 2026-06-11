"""summarizer — per-source digests, pinned to the local "cheap" tier.

Compression is volume work, not judgment work: it touches every note and
the whole feed every single morning, and the notes are private. Cheapest
capable model wins, and private text never leaves the machine.
"""

from agentkit import chat

_SYSTEM = (
    "You compress sources for a morning brief. For EACH source given, output "
    "exactly two lines and nothing else:\n"
    "SOURCE <filename>: <the single most important fact>\n"
    "ALSO: <the most decision-relevant detail — a deadline, open question, or number>"
)


def digest(notes: list[tuple], headlines: list[dict]):
    """One chat() call -> (digest_text, ChatResult)."""
    parts = [f"--- {name} ---\n{text.strip()[:1500]}" for name, text, _ in notes]
    if headlines:
        feed = "\n".join(f"- {h['title']}" for h in headlines)
        parts.append(f"--- headlines (today's feed) ---\n{feed}")
    r = chat("Digest each source:\n\n" + "\n\n".join(parts),
             system=_SYSTEM, provider="local", tier="cheap")
    return r.text.strip(), r
