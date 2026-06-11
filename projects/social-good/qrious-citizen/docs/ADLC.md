# ADLC Worksheet — qrious-citizen

## 1. Scope
A resident (or reporter, or councilor's aide) asks a plain-English question
about Boston open data; the agent returns a sourced, reproducible civic
brief. One end-to-end success case: "most rodent 311 complaints by
neighborhood last year → five-section brief with the dataset URL and the
rerunnable query." Out of scope: maps, rates/per-capita, multi-dataset
joins, anything needing an API key.

## 2. Design
One agent, three tools against the keyless CKAN API (data.boston.gov):
`search_datasets` (discovery — datasets are never hardcoded),
`get_records` (rows + deterministic tallies), `run_sql` (last resort; the
SQL endpoint is historically flaky, the skill says prefer get_records).
Every tool obeys the house fixture rule: AGENT_OFFLINE or ANY live failure
serves committed fixtures built from real June-2026 portal responses.
Model: local 3B (granite4:micro) — see docs/MODEL_SELECTION.md; the design
bet is that tallying in code makes a 3B sufficient.

## 3. Build
agentkit loop, 154 LOC, fixtures captured from live `package_search` /
`datastore_search` calls. The skill carries all format and method rules;
SYSTEM is role-only. Vibe-coded: the first SKILL.md wording. Engineered:
the `_summarize` tally (dedup, date span, top-N, Reproduce URL).

## 4. Evaluate  ← the loop ran 4 times; this log is the point
3 cases × with/without skill (`evals/evals.json`). Iteration log:
- **v1 bug (caught in the trace, not the eval):** with the skill loaded the
  model skipped `where='rodent'` and labeled the ALL-cases tally as "rodent
  complaints" — right format, wrong number (8 vs the true deduped 7).
  Fix in three places: tool docstring ("you MUST set where to that single
  word"), skill workflow re-worded, and unfiltered tallies now stamped
  "(NO filter: counts below cover ALL case types)".
- **v2 flake:** "The data" dropped the dataset URL in 1 of 2 runs. Fix:
  the template section became an exact-four-bullets contract ending
  "A brief with no dataset URL is unusable." Small models follow
  enumerated contracts better than prose lists.
- **v3 lesson:** findings came back as a numbered list and our `^[-*] `
  assertion counted 0 — the eval was testing a bullet GLYPH, not the
  outcome. Loosened to any list marker: **assert outcomes, not rituals**
  (the pilot learned the same thing).
- **Final:** with-skill 3/3, without-skill 0/3, delta +1.00. Across the 4
  full development runs the with-skill suite scored 3,2,2,3 — the two dips
  are the v2/v3 issues above, fixed rather than re-rolled.

## 5. Deploy
README quickstart; keyless live mode against data.boston.gov, `--offline`
for the no-wifi demo, fixtures double as the error fallback. Nothing to
configure beyond `ollama pull granite4:micro`.

## 6. Observe  ←
The run footer prints turns / tokens / $ / latency / tools-called; eval
outputs land in evals/outputs/ per case+mode. Two things traces taught us:
the v1 mislabeled-count bug was invisible to a green eval run and only
showed in the tool-call log (read your traces, not just your pass rates);
and live mode self-reported its own sampling ("analyzed 5000 of 14361")
straight into Caveats — the pagination gotcha firing for real.

## 7. Iterate
Next loop, in order: (1) month-bucket tallies in `_summarize` → trend
questions become answerable and testable; (2) a second fixture pair (food
inspections) to prove the skill generalizes across datasets; (3) frontier
row in MODEL_SELECTION.md — does sonnet fix the residual tool-arg variance
at acceptable cost?
