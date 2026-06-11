# ADLC Worksheet — wicked-smaht-bahtendah

## 1. Scope
Someone with a few ingredients and a vibe types one sentence; the agent
returns ONE complete recipe card — zero-proof unless alcohol was explicitly
requested. End-to-end success case: "mint and lime, hot day → Virgin Mojito
card, [zero-proof] tag, measures, shake/stir call." Out of scope: multi-drink
menus, batch scaling, inventory tracking, nutrition.

## 2. Design
One agent, two one-argument tools (`find_drinks_with`, `get_classic_recipe`
— single string args, the most reliable parameterized shape for a 3B), one
skill carrying ALL policy and format. Tools hit TheCocktailDB's keyless test
tier live and fall back to `fixtures/drinks-sample.json` (11 classics, the
API's exact strIngredientN/strMeasureN shape) on AGENT_OFFLINE or any
exception. Model: local granite4:micro — see docs/MODEL_SELECTION.md.

## 3. Build
agentkit loop, ~125 LOC. Fixture built from real live API responses plus two
hand-written zero-proof classics (Virgin Mojito, Shirley Temple) — the free
database doesn't carry them, which is itself the zero-proof gap this agent
fills. First SKILL.md draft was vibe-coded; everything after was eval- and
trace-driven.

## 4. Evaluate  ← 9 full suite runs + 3 live runs; this log is the point
3 cases × with/without skill (`evals/evals.json`). Iteration log:
- **v1 bug (eval):** the 3B degraded `## You need` into a bulleted
  `- **You need**`; the section parser rightly found nothing. Fix: "every
  heading is a `##` line — never a bullet, never bold" in the template
  intro. → 3/3 twice.
- **v2 bug (live trace):** the keyless tier truncates `filter.php` to ONE
  result — "lime" returned only "After Dinner Cocktail", and the model chased
  it for 7 turns into an EMPTY final answer. Fix (v3): a named classic skips
  ingredient search and goes straight to `get_classic_recipe`.
- **v3 bug (live trace):** the model fetched the Margarita, kept searching
  anyway, and recency bias served the LAST tool result (an After Dinner
  Cocktail). Fix (v4): stop rule — "write the card for the drink the user
  asked for, never for whatever a tool returned last." Live run after:
  2 turns, 4.3 s, correct drink.
- **v4 bug (eval):** case 3 copied Tequila Sunrise verbatim — tequila for a
  user who never asked for booze. The fetched classic was overriding the
  zero-proof default. Fix (v5): "the cabinet gives you proportions, not
  permission" gotcha + an explicit adapt step.
- **v5 flake (eval):** headers degraded to bold again AND numbered-bold
  steps (`1. **Prepare**`) — which the eval engine treats as pseudo-headings,
  truncating the section to zero lines. Fix (v6): restate the `##` rule at
  the END of the template, the model's highest-attention zone (the
  fridge-whisperer lesson, reused).
- **v6 flake (eval):** Tequila Sunrise again — spirit out of "You need" but
  still poured in "Build it". Fix (v7): prefer the already-non-alcoholic
  classic for zero-proof requests, and "no spirit named anywhere in the card
  except Switch it".
- **Final (v7):** with-skill 3/3, without-skill 0/3, delta +1.00, two
  consecutive clean runs. Residue, stated honestly: classic selection at 3B
  is stochastic (a re-roll can still draw Tequila Sunrise and leak), and the
  model sometimes lists a fixture extra the user lacks (ginger ale) — the
  eval asserts the named-ingredient floor and the no-spirits rule, not full
  inventory compliance. Named fixes: a deterministic zero-proof converter
  script, or a bigger model.

## 5. Deploy
README quickstart; runs keyless everywhere — live API needs no key, offline
needs no network, and `--offline` is the same demo with the same card.

## 6. Observe  ←
The run footer prints turns / tokens / $ / latency / tools-called on every
run; fallbacks print a one-line stderr notice naming the exception. What the
traces taught us: **two of the three real bugs (goose-chase, recency serve)
were only visible in live-run traces, never in offline evals** — measure
offline, but watch live.

## 7. Iterate
Next loop, in order: (1) `scripts/scale.py` deterministic batch math as a
third tool; (2) a `convert_zero_proof` script tool to move the residual
selection risk from model willpower to code; (3) same evals on granite3.3:8b
and one frontier model, table the deltas; (4) menu mode behind a second
skill (Lane 3 with fridge-whisperer).
