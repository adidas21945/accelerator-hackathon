---
name: routing-rationale
description: >-
  Formats a routed answer into a transparent receipt: the answer itself plus
  a table of models tried, self-graded confidence, escalation, estimated
  cost, and latency, then a plain-English read of the numbers. Use whenever
  presenting a cascade or routing result, explaining which model answered
  and why, justifying a model-selection or escalation decision, or
  reporting per-query cost and latency.
license: MIT
---

# Routing Rationale — the receipt behind every routed answer

A cascade router answers cheap-first and escalates only when unsure. That
decision is invisible unless you show it. This skill renders the receipt a
judge or teammate can audit: what was asked, which model answered, how sure
the cheap model was, what the query cost, and what the alternative would
have cost. The answer always comes first; the receipt explains it, never
replaces it.

## Defaults (do not present options)

- Costs are USD with 4 decimals; local model calls cost $0.0000.
- Confidence is the cheap model's self-grade, 0.00–1.00, two decimals,
  always shown next to the threshold it was compared against.
- Never claim frontier quality "wasn't needed" — say the self-confidence
  was above the threshold. The threshold is an economic setting, not a
  quality verdict.
- Copy every number verbatim from the routing facts. A missing fact is
  written "n/a" — never estimated, never invented.
- Latency is the total seconds for the whole cascade, as given in the facts.

## Workflow

1. Read the raw routing facts: models tried, self-confidence, threshold,
   escalated or not, estimated cost, latency, routing outcome, and the
   frontier-only comparison if given.
2. Write `## Answer`: the final answer exactly as given. Do not summarize,
   trim, or re-solve it.
3. Build the `## Routing decision` table strictly from the facts — one
   Field/Value row per fact, rows in the template's order.
4. Write `## What it means`: 1–2 sentences translating the numbers into a
   decision a teammate can audit — where the query resolved, what it cost,
   and what the alternative would have cost.

## Gotchas

- Self-grading flatters easy questions — that is fine and exactly why the
  cheap tier earns its keep. But a small local model over-trusts itself on
  everything, including reasoning traps (Monty-Hall-style puzzles): a
  confidently wrong answer never escalates. Measured: granite4:micro grades
  itself 0.90–1.00 across facts, puzzles, and haiku alike. Report
  confidence as what it is — the model's own opinion of its answer, never a
  correctness guarantee.
- Latency includes the self-grading call: a cascade spends two local calls
  before any escalation can happen. That overhead is the price of the
  pattern, so quote the total honestly rather than the answer call alone.
- Thresholds are economics, not truth: raising the threshold buys more
  frontier escalations, lowering it buys more $0.0000 answers. Neither
  setting makes any single answer more correct.
- "Escalation unavailable" (no frontier key, offline mode) is a legitimate
  routing outcome, not an error. Say the answer stayed local and why.

## Output template

Produce EXACTLY these sections, in this order:

## Answer
The final answer, verbatim from the facts you were given. No routing
commentary in this section.

## Routing decision
A markdown table, exactly these five Field/Value rows, values copied from
the routing facts:

| Field | Value |
|---|---|
| Model(s) tried | granite4:micro |
| Self-confidence | 0.85 (threshold 0.7) |
| Escalated | no |
| Est. cost this query | $0.0000 |
| Latency | 9.3 s |

## What it means
1–2 sentences translating the numbers. Match the sentence to the routing
outcome in the facts — one example per outcome:

- resolved locally: "Resolved locally at $0.0000 — self-confidence 0.85
  cleared the 0.7 threshold; a frontier-only setup would have paid ~$0.0042
  for the same answer."
- escalated: "Self-confidence 0.62 fell below the 0.9 threshold, so the
  query escalated to claude-opus-4-8; the answer cost $0.0214 instead of
  $0.0000."
- escalation unavailable: "Confidence 0.62 was below the 0.9 threshold, but
  no frontier key is configured, so the local answer stands at $0.0000."
