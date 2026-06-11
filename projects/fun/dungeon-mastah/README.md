# dungeon-mastah — the Boston-accented game master

> Theme: fun · Lane: L1 · Difficulty: 🦞 · Offline: fully · Keys: none

## Pitch

A tabletop GM agent that runs theater-of-the-mind one-shots — wicked funny,
a little dramatic, and *honest*, because the dice are real: a tested
deterministic script rolls them, and the skill forbids narrating an outcome
the table didn't see. Three agent lessons hide inside the fun: tested
`scripts/` doing the deterministic work (24 selftest checks on the dice
parser alone), session memory as nothing fancier than the saved message
transcript (`--save` / `--load` / `--play`), and a strict scene template
that keeps a 3B model punchy instead of rambling — enforced by code when
willpower fails (a truncated reply gets one fill-in turn; a dice-faking
reply gets one retake; the footer reports the true total spend).

## Quickstart

```bash
# from the repo root — local model by default (see docs/SETUP.md)
uv run python projects/fun/dungeon-mastah/agent.py \
  "Start a one-shot adventure in a haunted Boston brownstone."

# play on, scene by scene; blank line ends the session, --save keeps it
uv run python projects/fun/dungeon-mastah/agent.py "Start a heist one-shot." --play --save

# resume where you left off
uv run python projects/fun/dungeon-mastah/agent.py "We open the vault." --load

# baseline + evals
uv run python projects/fun/dungeon-mastah/agent.py "..." --no-skill
uv run python -m agentkit.evals projects/fun/dungeon-mastah
```

## Demo script (90 seconds)

1. `--play` a fresh one-shot. Read the opening scene aloud (the model has
   range — let it land).
2. Type an attack: `I kick open the cellar door and charge the ghoul!` —
   point at the stderr line showing the `roll_dice` tool call, then the SAME
   dice line quoted verbatim in the scene. Real dice, on the table.
3. `--save`, quit, `--load`, keep playing — session memory is just the
   transcript on disk; open `campaign/save.json` and show them.
4. Evals: with-skill 2/3 vs without-skill 0/3 — and without the skill there
   are no options, no party status, no rules. Structure is the game.

## Make it yours (extension ideas)

1. **Swap the genre** — the skill IS the setting: copy `campaign-rules`,
   rewrite the defaults (noir Boston 1926, space freighter, kaiju Beacon
   Hill), revalidate, play. Zero code changes.
2. **Initiative & combat subsystem** — extend `roll.py` with contested rolls
   and initiative order; keep it deterministic, keep the selftest growing.
3. **The lore-keeper** — a second agent + skill that maintains
   `campaign/world.md` between scenes (places, NPCs, promises made). Two
   agents, two skills, explicit hand-off = a Lane 3 build.
4. **Voice mode** — pipe scenes through TTS and play options by number;
   the template's numbered options were made for it.
5. **Harder dice honesty** — move the quote-the-roll rule fully into code:
   reject any scene whose dice lines don't match the tool log, retake until
   clean, and chart the retake rate per model tier.

## Rubric mapping

| Criterion (pts) | Where this starter already scores | What you still must do |
|---|---|---|
| Shippability (25) | runs from README; MIT; `agentskills validate` passes | your public repo + README |
| ADLC (20) | docs/ADLC.md — code-guards-over-willpower iteration story | re-run the loop on YOUR change |
| Model Selection (20) | local-only rationale + measured numbers; retake cost accounting | add your frontier comparison |
| Lane Merit (20) | end-to-end play, save/load memory, honest dice | your twist |
| Skill Quality (15) | triggers, defaults, gotchas, strict template, +0.67 delta | keep the delta positive |
