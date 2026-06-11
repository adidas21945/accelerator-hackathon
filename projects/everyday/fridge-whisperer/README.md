# fridge-whisperer — the what's-for-dinner agent

> Theme: everyday · Lane: L1 · Difficulty: 🦞 · Offline: fully · Keys: none

## Pitch

Tell it what's in your fridge; get back a weeknight dinner plan and a grocery
list you can actually shop from. The agent reads your pantry staples and diet
notes through two zero-argument tools (the most reliable tool shape for small
local models), and the `meal-plan` skill does the heavy lifting: hard
constraints from diet notes, purchasable quantities, and the #1 rule of meal
planners — staples never go on the grocery list. This is the gentlest starter
in the repo: no network, no keys, one skill, ~80 lines.

## Quickstart

```bash
# from the repo root — local model by default (see docs/SETUP.md)
uv run python projects/everyday/fridge-whisperer/agent.py \
  "I have chicken thighs, broccoli, and rice. Plan 3 dinners for 2 people."

# the eval baseline (no skill), and the house evals:
uv run python projects/everyday/fridge-whisperer/agent.py "..." --no-skill
uv run python -m agentkit.evals projects/everyday/fridge-whisperer
```

## Demo script (90 seconds)

1. Run the quickstart task. Point at the three template sections landing, and
   the run footer: turns, tokens, $0.00, latency, tools called.
2. Run it again with `--no-skill` — watch the structure (and the staples
   discipline) fall apart. That difference is the skill.
3. Open `evals/benchmark.json`: with-skill 2/3 vs without-skill 0/3 on a 3B
   local model (granite4:micro). The one flaky assertion is a genuine
   model-capability ceiling — see docs/ADLC.md for the iteration log, and
   "Make it yours" #1 for the fix.

## Make it yours (extension ideas)

1. **Make the staples rule mechanical** — add `scripts/strike_staples.py`
   (deterministic line filter) as a third tool; deterministic work belongs in
   scripts, not in a 3B model's willpower. Watch the eval go 3/3.
2. **Use-it-up mode** — "these 4 things expire by Friday" → plan that burns
   them down, soonest-expiring first.
3. **Swap the model tier** — same evals on granite3.3:8b or a frontier model
   via `MODEL_PROVIDER=anthropic`; put the pass-rate/cost/latency table in
   docs/MODEL_SELECTION.md. Instant Model Selection points.
4. **Pantry inventory agent** — second agent that maintains staples.txt from
   "we ran out of soy sauce" messages; two agents, two skills = Lane 3.
5. **Photo mode** — vision model reads the fridge shelf photo instead of a
   typed list.

## Rubric mapping

| Criterion (pts) | Where this starter already scores | What you still must do |
|---|---|---|
| Shippability (25) | runs from README; MIT; `agentskills validate` passes | your public repo + README |
| ADLC (20) | docs/ADLC.md is a real worked loop (3 iterations, evidence) | re-run the loop on YOUR change |
| Model Selection (20) | local-first rationale + measured numbers in docs/MODEL_SELECTION.md | add your frontier comparison |
| Lane Merit (20) | end-to-end on realistic input, honest eval delta | your twist |
| Skill Quality (15) | trigger-rich description, defaults, gotchas, template, +0.67 delta | keep the delta positive |
