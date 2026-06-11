# ADLC Worksheet — paypah-trail

## 1. Scope
You drop receipts in `receipts/` (text dumps, a PDF — whatever the month
produced); the agent returns a categorized monthly report with a CSV ledger.
One end-to-end success case: "Summarize my receipts for May 2026" over 6
sample receipts in 5 different real-world formats. Out of scope: OCR/photos,
multi-month history, budgets, bank feeds, tax categories.

## 2. Design
One agent, two tools — zero-arg `list_receipts` and one-arg
`parse_receipt(filename)` — and one skill carrying the categories, the
duplicate rule, and the exact report template. The design bet (the event
guide's "Form & Function" lesson): **the model never reads receipt bytes.**
A deterministic script with its own `--selftest` does vendor/date/total
extraction, because "which number is the total" is a regex problem, not a
reasoning problem. Model: local 3B (granite4:micro) — finances are private,
so the data never leaves the laptop. See docs/MODEL_SELECTION.md.

## 3. Build
agentkit loop (`run_agent`), ~90 LOC agent + ~140 LOC parser. The parser was
test-first (selftest mini-receipts written before the rules); the SKILL.md
draft was vibe-coded, then eval-corrected below. `make_sample_pdf.py` emits
the PDF sample in raw %PDF-1.4 syntax — no extra deps to build OR read it.

## 4. Evaluate  ← the loop ran; this log is the point
3 cases × with/without skill (`evals/evals.json`), one a `script` assertion
(`evals/check_csv.py`) that actually csv-parses the ledger block. Iteration log:
- **Parser first:** `parse_receipt.py --selftest` (6 mini-receipts: subtotal
  trap, post-tip AMOUNT DUE, 4 date formats, missing date, comma thousands,
  ALL-CAPS vendors) passed 6/6 before the agent ever ran. The restaurant
  rule — post-tip AMOUNT DUE beats pre-tip TOTAL — was selftest case 3.
- **v1 bug (2/3 with skill, 0/3 without, delta +0.67):** on "Which category
  did I spend the most on?" the model answered the question ad hoc — right
  answer, zero template sections, three failed assertions. The skill never
  said the template applies to *questions*, only implied it. Fix: a new
  FIRST default — "EVERY answer is the full four-section report, direct
  answer as the first words of ## Summary."
- **v2:** with-skill 3/3, without-skill 0/3, **delta +1.00.** Without the
  skill the model answers fluently but with no machine-readable structure —
  and on the summary case it silently dropped the duplicate receipt from
  its table, the exact failure the skill's gotcha exists for.
- **Deliberate call (the residual 3B ceiling):** we assert outcomes a report
  consumer needs (sections, a parseable ledger, the data-true top category,
  the duplicate named when asked) and do NOT assert the model's mental
  arithmetic — its grand total wobbled $299.99–$374.49 against the true
  $284.42 across passing runs while the per-receipt CSV stayed perfect,
  because those numbers are script-truth. Named fixes: a `sum_ledger`
  script tool, or a bigger model. Shipped honestly instead of asserted
  around.

## 5. Deploy
README quickstart; fully offline, zero keys, nothing to configure beyond
`ollama pull granite4:micro`. The parser CLI works standalone for skeptics:
`parse_receipt.py <file>` on any of the 6 samples.

## 6. Observe  ←
The run footer prints turns / tokens / $ / latency / tools-called every run.
What the traces taught us: granite4:micro makes exactly one tool call per
turn, so a 6-receipt month costs 8 turns — that's why `run()` sets
`max_turns=12`, and why "parse EVERY receipt" had to be a skill workflow
step, not a hope.

## 7. Iterate
Next loop, in order: (1) `sum_ledger` script tool so the one remaining
model-math step (category/grand totals) becomes deterministic too;
(2) same evals on granite3.3:8b and one frontier model, table the deltas;
(3) a no-date receipt sample to exercise the empty-date Flags path end-to-end.
