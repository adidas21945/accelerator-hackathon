# ADLC Worksheet — dungeon-mastah

*(Build note: the original builder was interrupted after its final benchmark;
this worksheet was completed by the integrator from the code, the eval
outputs, and a fresh verification run. The iteration evidence below is
visible in `agent.py`'s guard code and the benchmark history.)*

## 1. Scope
A table of 1+ players types actions; the agent GMs a PG-13 one-shot:
scenes, dice-resolved outcomes, party tracking, always-live options. One
end-to-end success case: start a brownstone one-shot → attack something →
the roll appears verbatim in the scene. Out of scope: persistent campaigns,
maps/minis, character creation, PvP.

## 2. Design
One agent, two tools — `roll_dice(spec)` (wraps the tested script; the only
source of randomness) and zero-arg `party_sheet()` — plus one skill carrying
tone, table rules, and the three-section scene template. Session memory is
the message transcript itself (`--save`/`--load`/`--play`). Model: local 3B;
the dice are code. See docs/MODEL_SELECTION.md.

## 3. Build
agentkit loop + ~60 lines of format-guard code. `roll.py` was written
test-first: 24 selftest checks (bounds ×300 rolls, seeding determinism,
sentence shape, and a parser fuzz list from `2d7` to `banana`).

## 4. Evaluate  ← the loop, as fought
3 cases × with/without skill. What the iterations fixed, in order:
- **Template compliance by willpower topped out ~70%** of takes on the 3B —
  replies truncated after the scene. Fix: a code-level dress code —
  `_missing()` detects absent/empty sections, one fill-in turn asks for ONLY
  those, and the sections are assembled in code (the take's own sections
  always win).
- **The genre tic**: "**What do you do?**" landing where `## Your options`
  belongs. Fix: mechanical canonicalization of that one line — content
  untouched, no second model call.
- **Faked dice**: narrated rolls that never touched the tool. Fix:
  `_dice_ok()` cross-checks every rolled line against the transcript and
  forbids tool-call text in prose; a failing take gets exactly ONE fresh
  retake, the better take ships, and the merged footer reports true spend.
- **Final benchmark: with-skill 2/3, without 0/3, delta +0.67.** The
  residual failure *moves between cases* run-to-run (dice-in-scene one run,
  numbered-options the next) — a genuine 3B variance ceiling, shipped
  honestly rather than re-rolled to 3/3.

## 5. Deploy
README quickstart; fully offline, zero keys; `--play` for live sessions.

## 6. Observe  ←
The stderr footer prints turns / tokens / $ / latency / tool calls, and —
because takes can merge — those numbers are the TRUE cost of the guards.
One thing the traces taught us: without the skill the model still loves to
narrate, but options, party status, and dice discipline simply vanish —
structure is the game, not the prose.

## 7. Iterate
Next loop: move dice honesty fully into code (reject-and-retake until the
tool log and scene agree, chart retake rate per model tier); try the same
evals on an 8B/frontier model — the variance ceiling should lift; add a
combat/initiative case to evals.json.
