# wicked-smaht-bahtendah — the zero-proof-by-default drink agent

> Theme: fun · Lane: L1 · Difficulty: 🦞 · Offline: fixtures (invention mode is fully offline) · Keys: none

## Pitch

Tell it what you have and the vibe; get back ONE proper recipe card — name,
measures in oz (ml), shake-or-stir build, a twist, and the boozy↔zero-proof
conversion line. The `recipe-card` skill is the event's "defaults, not menus"
rule made delicious: every drink is **zero-proof unless you explicitly ask
for alcohol** — "refreshing" is not a request for rum. Two one-argument tools
search TheCocktailDB's free keyless tier when the wifi is up, fall back to a
committed 11-classic fixture cabinet when it isn't, and pure invention mode
needs no data at all.

## Quickstart

```bash
# from the repo root — local model by default (see docs/SETUP.md)
uv run python projects/fun/wicked-smaht-bahtendah/agent.py \
  "Something refreshing with mint and lime for a hot day."

# without the skill (the eval baseline), or fully offline:
uv run python projects/fun/wicked-smaht-bahtendah/agent.py "..." --no-skill
uv run python projects/fun/wicked-smaht-bahtendah/agent.py "..." --offline

# the house evals (always offline, writes evals/benchmark.json):
uv run python -m agentkit.evals projects/fun/wicked-smaht-bahtendah
```

## Demo script (90 seconds)

1. Run the quickstart task. Point at the **[zero-proof]** tag on the card:
   nobody asked for alcohol, so none was served — a default, not a menu of
   "would you like the virgin or classic version?".
2. Run `"Make me a proper boozy margarita."` — an explicit ask gets real
   tequila, real measures, a salt rim, and a "Switch it" line back to
   zero-proof. Live, this is one tool call and ~2 turns.
3. Kill the wifi (or just add `--offline`): same demo, same card — the
   fixture cabinet answers, and the footer proves nothing else changed.
4. Open `evals/benchmark.json`: with-skill 3/3 vs without-skill 0/3 on a 3B
   local model (granite4:micro), delta +1.00. The seven-version iteration
   log behind that number is in docs/ADLC.md.

## Make it yours (extension ideas)

1. **Party-batch math** — add `scripts/scale.py`, a deterministic oz→ml→
   bottles converter for N guests, as a third tool. Scaling measures is
   arithmetic; arithmetic belongs in a script, not in a 3B model's head.
2. **Menu mode** — "tiki night for 8" → three cards: one zero-proof, one
   classic, one pun-named invention, with a shared shopping list.
3. **Pair with fridge-whisperer** — feed its dinner plan in and return a
   matched drink per dinner. Two agents, two skills, one pipeline = Lane 3.
4. **Taste-profile memory** — persist "less sweet, loves ginger" to a notes
   file the agent reads first, fridge-whisperer-style, and bias every card.

## Rubric mapping

| Criterion (pts) | Where this starter already scores | What you still must do |
|---|---|---|
| Shippability (25) | runs from README; MIT; `agentskills validate` passes; live API fails soft to fixtures | your public repo + README |
| ADLC (20) | docs/ADLC.md logs 7 skill versions, 9 eval runs, 3 live-run bugs found and fixed | re-run the loop on YOUR change |
| Model Selection (20) | local-first rationale + measured numbers in docs/MODEL_SELECTION.md | add your frontier comparison |
| Lane Merit (20) | end-to-end on realistic input; the defaults beat lands on a 3B | your twist |
| Skill Quality (15) | trigger-rich description, hard defaults, bartender gotchas, exact template, +1.00 delta | keep the delta positive |

---

*The default is zero-proof on purpose: the best host serves everyone first
and the bar cart second. Keep it classy — and if you do pour, pour for
people who are 21+.*
