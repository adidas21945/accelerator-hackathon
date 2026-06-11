"""wicked-smaht-bahtendah — the zero-proof-by-default drink agent.

A mixology agent that turns "what I have + the vibe" into one proper recipe
card. The skill carries the event's defaults-not-menus rule in delicious
form: every drink is ZERO-PROOF unless the request explicitly asks for
alcohol. Two one-argument tools search TheCocktailDB's free keyless tier
when the network is up and fall back to a committed fixture cabinet when it
isn't — and pure invention mode needs no data at all.
"""

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Self-locate the repo root: plain `python agent.py` works from anywhere,
# no editable install or cwd assumptions.
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "agentkit").is_dir())))

from agentkit import run_agent, tool  # noqa: E402

DEFAULT_SKILL = HERE / "skills" / "recipe-card"
API = "https://www.thecocktaildb.com/api/json/v1/1"

SYSTEM = (
    "You are Wicked Smaht Bahtendah, a friendly Boston mixology agent. "
    "Check the cabinet with your tools for a matching classic before you "
    "invent a drink."
)


def _cabinet() -> list:
    """The committed fixture cabinet: ~10 classics in the API's field shape."""
    return json.loads((HERE / "fixtures" / "drinks-sample.json").read_text())["drinks"]


def _ingredients(d: dict):
    """Yield (ingredient, measure) pairs from a strIngredientN/strMeasureN record."""
    for i in range(1, 16):
        ing = (d.get(f"strIngredient{i}") or "").strip()
        if ing:
            yield ing, (d.get(f"strMeasure{i}") or "").strip()


def _card(d: dict) -> str:
    """One drink record -> one compact sentence the model can adapt."""
    parts = [f"{ing} ({mea})" if mea else ing for ing, mea in _ingredients(d)]
    return (
        f"{d['strDrink']} [{d.get('strAlcoholic', 'Unknown')}] — serve in a "
        f"{d.get('strGlass', 'glass').lower()}. Ingredients: {'; '.join(parts)}. "
        f"Method: {(d.get('strInstructions') or '').strip()}"
    )


@tool
def find_drinks_with(ingredient: str):
    """Search the drinks cabinet for classic drinks that use one ingredient, e.g. 'lime', 'mint', 'tequila'. Use this first to find a classic worth adapting."""
    if not os.getenv("AGENT_OFFLINE"):
        try:
            import requests

            r = requests.get(f"{API}/filter.php", params={"i": ingredient}, timeout=10)
            r.raise_for_status()
            drinks = (r.json() or {}).get("drinks")
            if isinstance(drinks, list) and drinks:
                names = ", ".join(d["strDrink"] for d in drinks[:8])
                return f"Classics in the cabinet that use {ingredient}: {names}."
        except Exception as e:
            print(f"[wicked-smaht-bahtendah] live cabinet unreachable ({type(e).__name__}); using the local fixture.", file=sys.stderr)
    names = [d["strDrink"] for d in _cabinet()
             if any(ingredient.lower() in ing.lower() for ing, _ in _ingredients(d))][:8]
    if names:
        return f"Classics in the cabinet that use {ingredient}: {', '.join(names)}."
    return f"No classic in the cabinet uses {ingredient} — invent something using the skill's rules."


@tool
def get_classic_recipe(name: str):
    """Look up one classic drink recipe by name, e.g. 'Margarita' or 'Virgin Mojito'. Returns its ingredients with measures, method, and glass."""
    if not os.getenv("AGENT_OFFLINE"):
        try:
            import requests

            r = requests.get(f"{API}/search.php", params={"s": name}, timeout=10)
            r.raise_for_status()
            drinks = (r.json() or {}).get("drinks")
            if isinstance(drinks, list) and drinks:
                return _card(drinks[0])
        except Exception as e:
            print(f"[wicked-smaht-bahtendah] live cabinet unreachable ({type(e).__name__}); using the local fixture.", file=sys.stderr)
    for d in _cabinet():
        if name.lower() in d["strDrink"].lower():
            return _card(d)
    return f"{name} is not in the local cabinet — invent something using the skill's rules."


def run(task: str, skill=DEFAULT_SKILL):
    """The agent contract every project honors: run(task, skill=...) -> AgentResult."""
    return run_agent(
        task,
        tools=[find_drinks_with, get_classic_recipe],
        skill=skill,
        system=SYSTEM,
    )


def main():
    ap = argparse.ArgumentParser(description="Wicked Smaht Bahtendah — drink recipe-card agent")
    ap.add_argument("task", help='e.g. "Something refreshing with mint and lime for a hot day."')
    ap.add_argument("--no-skill", action="store_true", help="run without the skill (the eval baseline)")
    ap.add_argument("--offline", action="store_true", help="force fixture mode (no network, same demo)")
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
