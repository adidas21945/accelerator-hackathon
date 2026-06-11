# ADLC Worksheet — chief-of-stuff

## 1. Scope
A working person points the agent at a briefcase/ of their actual life
(calendar.ics, todos.md, meeting notes, a news feed) and gets the one page
that matters at 7am. One end-to-end success case: "Build my morning brief
for Friday, June 26, 2026" — where a todo ("send the revised proposal"),
the 09:00 client sync, and a note's deadline ("before Friday's 09:00 sync")
must compose into priority #1. Out of scope (be brutal): email, writing the
proposal itself, multi-person calendars, timezone math beyond what the .ics
says, anything that edits the briefcase.

## 2. Design
Hub-and-spoke (see README diagram): orchestrator → ingest (deterministic
code) → summarizer (local/cheap) → prioritizer (strong tier, graceful local
fallback) → researcher (local/cheap) → one final local render through a
skill. Delegation is plain function calls — readable in twenty lines of
`run_brief()`, no framework. Two skills: morning-brief (the product) and
meeting-prep (the composition story: same specialists, second template).
Model per task + why → docs/MODEL_SELECTION.md.

## 3. Build
agentkit `chat()` per specialist — no tool loop, because the hub IS the
control flow; a 3B never has to decide what to call next. 466 lines across
agent.py + agents/ (budget: 500). The briefcase fixtures and the first
SKILL.md drafts were vibe-coded; everything after iteration v1 below was
eval-driven.

## 4. Evaluate  ← the loop ran 3 times; this log is the point
3 cases × with/without skill (`evals/evals.json`; the without-skill baseline
strips the skill from the FINAL render only — specialists still run, so the
skill template is the only variable). Iteration log:

- **v1 (smoke run) bugs:** the renderer dropped the 11:00 1:1 from
  "## Today"; "## Loose ends" dumped all 8 remaining todos with no stale
  flag; the prioritizer ranked prep-work above the deadline-bound proposal.
  Fixes: assembly now labels the schedule "ground truth — every line below
  belongs in the brief"; the skill's Defaults gained "lists EVERY calendar
  item (never drop one)" and a hard Loose-ends cap; the prioritizer's
  system prompt gained "a hard deadline tied to one of TODAY'S meetings
  outranks everything else."
- **v2 (case-1 sanity eval):** with-skill 8/8 assertions, without-skill
  1/8. All four events listed. Loose ends still drifts between 4 and 8
  bullets run to run — we assert outcomes (sections, citations, times,
  no invented meetings), not bullet counts, on purpose.
- **v3 (full run):** with-skill **3/3**, without-skill **0/3**, delta
  **+1.00** (evals/benchmark.json). Best evidence in the outputs: the
  without-skill Saturday brief hallucinated a "Client Sync Meeting at
  09:00" onto Saturday; the with-skill run lists only Agent Build Day.
  That is the skill's "calendar is truth / never invent meetings" gotcha,
  measurably doing its job. The July-2 decoy event ("Quarterly board
  review") never leaked into any June-26 brief — the never-invent
  `not_regex` stayed green in all six runs.
- **Residual (shipped honestly):** the local-fallback prioritizer sometimes
  ranks the proposal #3 instead of #1. Two named fixes: export
  `ANTHROPIC_API_KEY` (the strong tier exists for exactly this call), or
  add deterministic deadline extraction to ingest so code, not model
  willpower, hoists hard deadlines.

## 5. Deploy
README quickstart is two commands (brief + --prep), offline by default,
zero keys. deploy/zeroclaw/ has a parseable config + cron recipe for
scheduled 7am delivery; deploy/openclaw/ shows the skills dropping into a
personal agent gateway, with the security caveat that section earns.

## 6. Observe  ←
The instrument IS the routing table: every run prints per-agent model,
route, tokens, $, latency to stderr, plus a one-line totals footer. Three
things the traces taught us: (1) ~80% of tokens are template work — only
the prioritizer is quality-bound, so locality is free; (2) under Ollama
contention the same case ranged 11–81s — never quote demo timings you
measured once; (3) printing `strong→local fallback (no key)` in the table
turns model-selection from a docs claim into a per-run artifact judges can
see.

## 7. Iterate
What the loop changed: two skill-Default rules, one prioritizer rule, one
assembly label (v1); an outcomes-not-counts assertion philosophy (v2). Day
two, in order: (1) deterministic deadline extraction in ingest — move the
residual ranking failure from model willpower to code; (2) the same evals
with a frontier prioritizer, table the Top-3 quality delta; (3) a fourth
specialist (email digest via MCP) — one more routing-table row; (4) fan
out --prep across every meeting on the calendar before 7am.
