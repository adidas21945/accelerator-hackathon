# qrious-citizen — civic questions in, sourced briefs out

> Theme: social good · Lane: L1 · Difficulty: 🦞🦞 · Offline: fixtures · Keys: none

## Pitch

Ask a question about Boston open data — "Which neighborhoods had the most
rodent 311 complaints last year?" — and get a five-section civic brief with a
headline number, the dataset URL, quantified findings, honest caveats, and the
exact query to rerun. The agent discovers datasets on Analyze Boston
(data.boston.gov, a keyless CKAN API) and pulls rows; counting is done
deterministically in the tools (a 3B should never tally 5,000 rows), and the
`civic-brief` skill does the rest: duplicate filtering, pagination honesty,
reporting-bias caveats, and the exact output format. Deliberate adaptation
from the event doc's version of this project: that one calls the raw
`anthropic` SDK; this one rides agentkit so ONE code path serves
local/Anthropic/OpenAI/Gemini, and it prefers `datastore_search` over the
historically flaky SQL endpoint.

## Quickstart

```bash
# from the repo root — local model by default, live data.boston.gov (keyless)
uv run python projects/social-good/qrious-citizen/agent.py \
  "Which neighborhoods had the most rodent 311 complaints in Boston last year?"

# without the skill (the eval baseline), or fully offline (committed fixtures):
uv run python projects/social-good/qrious-citizen/agent.py "..." --no-skill
uv run python projects/social-good/qrious-citizen/agent.py "..." --offline

# the house evals (always offline, writes evals/benchmark.json):
uv run python -m agentkit.evals projects/social-good/qrious-citizen
```

## Demo script (90 seconds)

1. Run the quickstart task live: the agent searches the portal, pulls ~5,000
   real rows, and the brief lands with real numbers (Dorchester led with 897
   rodent cases in our test run) — plus a Caveats bullet admitting the 5,000
   of 14,361 sampling. That caveat is the skill's pagination gotcha working.
2. Kill the wifi and add `--offline` — same brief shape from committed
   fixtures (42 realistic rows; live calls also fall back here on any error).
3. Run with `--no-skill`: structure, dataset URL, and caveats all evaporate.
4. Open `evals/benchmark.json`: with-skill 3/3 vs without-skill 0/3 on a 3B
   (granite4:micro), delta +1.00. The iteration log that got it there is in
   docs/ADLC.md.

## Make it yours (extension ideas)

1. **Trend briefs** — tally by month in `_summarize` and answer "are rodent
   complaints rising?"; the incomplete-current-month gotcha is already there.
2. **Second dataset** — food inspections or crime incidents: same skill, one
   new fixture pair, zero agent changes (search already discovers them).
3. **Rates mode** — join a neighborhood-population fixture and flip the
   skill's counts-not-rates default into per-1,000-residents briefs.
4. **Frontier comparison** — `MODEL_PROVIDER=anthropic` on the same evals;
   put the cost/latency/pass-rate row in docs/MODEL_SELECTION.md.
5. **Weekly watch** — cron the rodent brief every Monday and post it to a
   neighborhood Slack; a civic newsletter nobody has to write.

## Rubric mapping

| Criterion (pts) | Where this starter already scores | What you still must do |
|---|---|---|
| Shippability (25) | runs from README, live or offline; MIT; `agentskills validate` passes | your public repo + README |
| ADLC (20) | docs/ADLC.md logs 3 real fix iterations with evidence | re-run the loop on YOUR change |
| Model Selection (20) | local-first rationale + measured numbers; counting moved out of the model | add your frontier comparison |
| Lane Merit (20) | end-to-end on live city data, keyless, honest sampling caveats | your twist |
| Skill Quality (15) | trigger-rich description, defaults, 4 gotchas, references/ + assets/, +1.00 delta | keep the delta positive |
