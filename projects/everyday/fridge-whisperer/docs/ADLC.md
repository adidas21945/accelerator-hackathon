# ADLC Worksheet — fridge-whisperer

## 1. Scope
A busy household member types ingredients + constraints; the agent returns a
multi-day dinner plan and a buy-only grocery list. One end-to-end success
case: "chicken thighs, broccoli, rice → 3 dinners for 2." Out of scope:
breakfast/lunch, full recipe steps, nutrition math, price data.

## 2. Design
One agent, two zero-argument read tools (`read_pantry_staples`,
`read_diet_notes` — no-arg tools are the most reliable shape for small local
models), one skill carrying ALL format and rules. Model: local 3B
(granite4:micro) because the data is personal (allergies) and the task is
template-bound, not reasoning-bound. See docs/MODEL_SELECTION.md.

## 3. Build
agentkit loop (`run_agent`), ~80 LOC. The first SKILL.md draft was
vibe-coded; everything after iteration 1 below was eval-driven.

## 4. Evaluate  ← the loop ran 3 times; this log is the point
3 cases × with/without skill (`evals/evals.json`). Iteration log:
- **v1 bug:** the skill's output template listed "Pantry" as a grocery-list
  aisle — the model dutifully filed soy sauce and salt UNDER it. Fix: rename
  the aisle, add the gotcha "not even under a 'pantry' heading."
- **v2 bug:** "olive oil" still leaked onto lists ~50% of runs. Fix: enumerate
  the staples inside the output-template section (the model's
  highest-attention zone), not just in Gotchas.
- **v3 lesson:** we briefly asserted the skill's literal "Staples check:
  passed" line — it flaked while the actual staples rule held. Dropped it:
  **assert outcomes, not rituals.**
- **Final:** with-skill 2/3, without-skill 0/3, delta +0.67. The residual
  failure moves between assertions run-to-run — a genuine 3B ceiling, with
  two named fixes (deterministic strike-staples script tool, or a bigger
  model). Shipped honestly rather than re-rolled to 3/3.

## 5. Deploy
README quickstart; runs offline with zero keys on any OpenAI-compatible
local endpoint; nothing to configure beyond `ollama pull granite4:micro`.

## 6. Observe  ←
The run footer prints turns / tokens / $ / latency / tools-called on every
run. One thing the traces taught us: **without the skill, runs are ~2×
slower** — no output template means the 3B rambles. Structure is speed.

## 7. Iterate
Next loop, in order: (1) `scripts/strike_staples.py` as a deterministic tool
— move the flaky rule from model willpower to code; (2) same evals on
granite3.3:8b and one frontier model, table the deltas; (3) a "use-it-up"
expiring-ingredients case.
