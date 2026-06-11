"""Manual smoke: prove the agent loop completes a tool call on YOUR model.

Run:  uv run python tests/manual_loop_smoke.py
This is the 30-second 'is my setup working' check from docs/SETUP.md.
"""

import sys
from pathlib import Path

# Self-locate the repo root so this runs with plain `python` from anywhere —
# no editable install or cwd assumptions (the house pattern; every agent.py does this).
_root = next(p for p in Path(__file__).resolve().parents if (p / "agentkit").is_dir())
sys.path.insert(0, str(_root))

from agentkit import run_agent, tool


@tool
def secret_number(city: str):
    """Look up the secret number for a city. Use this whenever asked about secret numbers."""
    # Sentence-shaped tool results land far better with small local models
    # than bare values do — a pattern every project's tools follow.
    return f"The secret number for {city} is {sum(map(ord, city)) % 100}."


if __name__ == "__main__":
    r = run_agent("What is the secret number for Boston? Use your tool, then answer with just the number.",
                  tools=[secret_number], max_turns=4)
    expected = str(sum(map(ord, "Boston")) % 100)
    print(f"\nanswer: {r.text.strip()[:120]}")
    print(f"turns={r.turns} tool_calls={[c[0] for c in r.tool_calls]} "
          f"tokens={r.usage} cost=${r.cost_usd} latency={r.latency_s}s")
    ok = any(c[0] == "secret_number" for c in r.tool_calls) and expected in r.text
    print("SMOKE PASS" if ok else f"SMOKE FAIL (expected {expected} via secret_number tool)")
    raise SystemExit(0 if ok else 1)
