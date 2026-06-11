# storm-ready — the household storm-readiness agent

> Theme: social good · Lane: L1 · Difficulty: 🦞🦞 · Offline: fixtures · Keys: none

## Pitch

Give it a place; it checks live National Weather Service alerts and the point
forecast, and hands back a brief a household can act on in ten minutes —
what's happening, what to do first, what to pack. Built for community
resilience: regular families, elderly neighbors, community groups. The
`storm-prep` skill carries the judgment: a calm voice, an all-clear brief as
a first-class result (no invented drama on quiet days), go-bag contents tuned
to the actual hazard, and the NWS API's two famous traps (mandatory
User-Agent header, the points→gridpoint two-step) sealed inside the tools.
Offline mode serves a recorded Hurricane Arthur alert set from `fixtures/`,
so the severe-weather demo works with no wifi — fitting, for a storm tool.

## Quickstart

```bash
# from the repo root — local model by default, live NWS data
uv run python projects/social-good/storm-ready/agent.py \
  "Build a storm-readiness brief for Boston, MA."

# the recorded severe event (Hurricane Arthur fixtures), no network needed:
uv run python projects/social-good/storm-ready/agent.py "Are we okay in Suffolk County this weekend?" --offline

# the eval baseline (no skill), and the house evals:
uv run python projects/social-good/storm-ready/agent.py "..." --no-skill
uv run python -m agentkit.evals projects/social-good/storm-ready
```

## Demo script (90 seconds)

1. **Live mode** (no flag): run the quickstart task. In late June the real
   answer is usually quiet — an all-clear brief, or a heat advisory briefed
   as heat (the alerts feed is all-hazards, and the agent doesn't pretend
   it's a storm). Calm is correct behavior, and it's asserted in the evals.
2. **Offline mode** (`--offline`): same question, now against the recorded
   Hurricane Arthur warning set — watch the same five sections turn urgent:
   Extreme/Severe alerts in "Situation", 60 mph gusts in "Next 48 hours", a
   hurricane go-bag. That live-vs-severe contrast is the demo beat.
3. Run the evals; open `evals/benchmark.json`: with-skill 3/3 vs
   without-skill 0/3 on granite4:micro — a +1.00 pass-rate delta.
4. Bonus: point at the run footer (turns, tokens, $0.00, latency, tools) and
   the stderr notice when live NWS is unreachable — it degrades to fixtures
   instead of dying, which is exactly what an emergency tool should do.

## Make it yours (extension ideas)

1. **FEMA layer** — add OpenFEMA Disaster Declarations (keyless, `$filter`
   API: `https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$filter=state eq 'MA'`)
   as a third tool, so the brief knows when a county is already under a
   federal declaration.
2. **Multilingual brief** — translate the skill's output template (one skill
   directory per language) and let the task's language pick it; readiness
   info fails exactly where English-only does.
3. **SMS-length mode** — a 320-character digest section for the neighbor
   without a smartphone; assert the length with a `script` eval.
4. **Town shelter list** — a zero-argument tool reading your town's open-data
   shelter/cooling-center list, folded into "Do now".
5. **Tier the storm** — route quiet days to the local 3B and Extreme-severity
   days to a frontier model via `agentkit.route.cascade`; put the measured
   table in docs/MODEL_SELECTION.md.

## Rubric mapping

| Criterion (pts) | Where this starter already scores | What you still must do |
|---|---|---|
| Shippability (25) | runs from README; MIT; `agentskills validate` passes; degrades to fixtures on network failure | your public repo + README |
| ADLC (20) | docs/ADLC.md logs a real eval-driven loop (the Unicode-typography bug hunt) | re-run the loop on YOUR change |
| Model Selection (20) | offline-first local rationale + measured numbers in docs/MODEL_SELECTION.md | add your frontier comparison |
| Lane Merit (20) | live government data end-to-end for community resilience; honest all-clear mode | your twist |
| Skill Quality (15) | trigger-rich description, defaults, 5 gotchas (2 API, 3 judgment), exact template, +1.00 delta | keep the delta positive |
