# paypah-trail — the receipts-to-ledger agent

> Theme: everyday · Lane: L1 · Difficulty: 🦞🦞 · Offline: fully · Keys: none

## Pitch

Drop receipts in a folder — messy grocery tape, a minimal coffee slip, SKU-heavy
hardware, a tipped restaurant check, even a PDF — and ask for a monthly summary:
categorized spending plus a machine-readable CSV ledger. The design lesson is the
event guide's "Form & Function" pattern, applied: a TESTED deterministic script
(`parse_receipt.py --selftest`) does ALL the byte-level parsing — vendor, date,
the subtotal-vs-total trap — and the model never gropes through receipt bytes;
the 3B only categorizes and assembles. The privacy story is the pitch: your
finances never leave the laptop. Local model, no keys, no network, $0.00.

## Quickstart

```bash
# from the repo root — local model by default (see docs/SETUP.md)
uv run python projects/everyday/paypah-trail/agent.py \
  "Summarize my receipts for May 2026."

# prove the parser without any model at all:
uv run python projects/everyday/paypah-trail/skills/expense-report/scripts/parse_receipt.py --selftest
uv run python projects/everyday/paypah-trail/skills/expense-report/scripts/parse_receipt.py \
  projects/everyday/paypah-trail/receipts/receipt-05-pharmacy.pdf

# the eval baseline (no skill), and the house evals:
uv run python projects/everyday/paypah-trail/agent.py "..." --no-skill
uv run python -m agentkit.evals projects/everyday/paypah-trail
```

## Demo script (90 seconds)

1. `cat` two receipts — the lowercase coffee slip and the restaurant check with
   a tip line — then run the parser CLI on each: same clean JSON either way,
   and the restaurant total is the post-tip AMOUNT DUE, not the pre-tip TOTAL.
   That's deterministic code doing the work a model fumbles.
2. Run the quickstart task. Point at the tool trace (one `parse_receipt` per
   file, PDF included), the four template sections, the CSV ledger, and the
   duplicate coffee receipt called out in "## Flags". Footer: $0.00, local.
3. Run the evals: with-skill 3/3 vs without-skill 0/3 in `evals/benchmark.json`
   — the delta is the skill. Mention the honest ceiling: the 3B's category
   *arithmetic* can wobble (see docs/ADLC.md); the ledger numbers can't,
   because they come from the script.

## Make it yours (extension ideas)

1. **Make the sums mechanical too** — add a `sum_ledger` script tool that
   totals parsed receipts per category, so even the arithmetic leaves the
   model's hands. Same lesson, second act (this is the 3B's one weak spot).
2. **Photo receipts** — OCR via a vision model that emits the same JSON, as an
   extension, NOT core: the deterministic parser stays the source of truth.
3. **Watch-folder daemon** — loop on `receipts/`, re-run on new files, append
   to a running ledger.csv.
4. **Budget thresholds** — a budgets.yaml plus a Flags rule: "Dining is 40%
   over budget" alerts in the report.
5. **Export to Sheets via MCP** — push the ledger to a spreadsheet; the CSV
   block is already the interchange format.

## Rubric mapping

| Criterion (pts) | Where this starter already scores | What you still must do |
|---|---|---|
| Shippability (25) | runs from README; MIT; `agentskills validate` passes | your public repo + README |
| ADLC (20) | docs/ADLC.md is a real worked loop with evidence | re-run the loop on YOUR change |
| Model Selection (20) | privacy-bound local rationale + measured numbers in docs/MODEL_SELECTION.md | add your frontier comparison |
| Lane Merit (20) | end-to-end on 6 realistic receipts incl. a PDF, honest eval delta | your twist |
| Skill Quality (15) | trigger-rich description, defaults, gotchas, exact template, script-backed workflow | keep the delta positive |
