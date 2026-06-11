---
name: expense-report
description: >-
  Parses receipt files with a deterministic script and assembles a monthly
  expense report with a CSV ledger. Use whenever asked to summarize receipts
  or expenses, break down or total spending by category or by month, build a
  spending ledger, or find duplicate or suspicious receipts.
license: MIT
---

# Expense Report from a Receipts Folder

Turn a folder of raw receipts into one trustworthy monthly report. The
tested script behind `parse_receipt` does ALL the reading — vendor, date,
total — so every dollar in the report comes from deterministic code, never
from a model squinting at receipt bytes. Your job is only to categorize,
add up, and assemble.

## Defaults (do not present options)

- EVERY answer is the full four-section report below — even a single
  question ("which category is top?", "any duplicates?") gets all four
  sections, with the direct answer as the first words of "## Summary".
- Categories are EXACTLY: Groceries, Dining, Transport, Health, Home, Other.
  Never invent another category; when unsure, use Other.
- The report month is inferred from the receipt dates — never ask.
- Amounts are always dollars with exactly 2 decimals (e.g. $9.75).
- Every receipt appears exactly once in the ledger, even flagged ones.

## Workflow

1. Call `list_receipts` to see what is in the folder.
2. Call `parse_receipt` on EVERY file, one at a time — .txt and .pdf alike.
   Never read or guess receipt contents yourself; the script handles every
   format and already applies the total-picking rules.
3. Categorize each receipt by vendor and contents. The parser's
   `category_hint` is usually right; override it only with a clear reason.
4. Add up per-category and grand totals from the parsed `total` values
   only, then write the report exactly per the output template.

## Gotchas

- Subtotal vs total: the script already picks the true total (the largest
  TOTAL / AMOUNT DUE line, never SUBTOTAL) — do not second-guess it and do
  not re-add tax.
- Tips are part of the meal: a restaurant total that includes the tip
  counts fully under Dining.
- Two receipts with the same vendor, date, AND total = a possible
  duplicate. Keep both ledger rows and count both in the totals, but say so
  in "## Flags" — never double-count silently.
- A receipt with no date stays in the ledger with an empty date field and
  is listed under "## Flags" — never guess a date.

## Output template

Produce EXACTLY these sections, in this order, for every request:

## Summary
One sentence: N receipts, $X.XX total spending, and the top category —
plus, if the user asked a specific question, its direct answer first.

## By category
One bullet per non-empty category, largest first:
"Category — $X.XX (n receipts)".

## Ledger
A ```csv fenced code block: header line `date,vendor,category,total`, then
one row per receipt (date as YYYY-MM-DD, total as a plain number like 74.49).

## Flags
Bullets for anything missing, duplicated, or odd. If nothing, write exactly
"Nothing flagged."
