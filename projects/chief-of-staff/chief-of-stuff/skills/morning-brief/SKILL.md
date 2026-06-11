---
name: morning-brief
description: >-
  Renders gathered briefcase facts (schedule, ranked priorities, source
  digests, reading candidates) into the one-page 7am morning brief. Use
  whenever asked for a morning brief, daily brief, "what does my day look
  like", "what matters today", or to assemble priorities, schedule, meeting
  prep, and reading into a single page.
license: MIT
---

# Morning Brief

Turn pre-digested briefcase facts into the one page a busy person actually
reads at 7am, coffee in hand. You are the last step in a pipeline: the facts
arrive already gathered, ranked, and cited. Your job is ruthless selection
and exact formatting — not research, not re-ranking.

## Defaults (do not present options)

- Top-3 priorities MAX. A list of 7 priorities is a todo list, not a brief.
- Every priority cites its source file in parentheses — (todos.md),
  (2026-06-25-client-sync.md). No citation, no slot.
- The schedule is chronological, lists EVERY calendar item for the date
  (never drop one), and every line starts with its HH:MM time.
- Loose ends caps at 3 todos plus the oldest stale note. Never dump the
  whole backlog there.
- The whole brief fits one screen: about 250 words. Cut detail, never cut
  sections.

## Workflow

1. Priorities first: copy the three ranked priorities, keeping their order
   and their (source) citations.
2. Schedule second: every calendar line for the date, in time order.
3. Meeting prep third: for each meeting, the ONE thing to have ready.
4. Reading last: only what was marked relevant; when nothing was, say so.

## Gotchas

- The calendar is truth. A todo that conflicts with the calendar loses.
- NEVER invent meetings, deadlines, or attendees that are not in the
  provided facts. An empty line beats a confident guess.
- "Worth a read" is optional — empty beats filler. Never pad it to three.
- Stale notes (older than a week) get a staleness flag, e.g. "(16 days old —
  reconfirm)", never silent trust.

## Output template

Produce EXACTLY these five sections, in this order, with these headings:

## Top 3
Numbered 1.–3., each line: action — why it must happen today (source-file).

## Today
One line per calendar item: HH:MM — title (people, if any). Time order.

## Meeting prep
One bullet per meeting today: the ONE thing to have ready when it starts.

## Worth a read
Up to 3 bullets, "headline — why it matters today". If nothing was marked
relevant, write exactly: Nothing essential today.

## Loose ends
EXACTLY 3 bullets or fewer: open todos that can safely slip today. Then one
final bullet for the oldest stale note with its flag, e.g.
"2026-06-10-q3-planning.md (16 days old — reconfirm before reusing)".
