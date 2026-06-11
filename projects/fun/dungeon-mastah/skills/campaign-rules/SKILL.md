---
name: campaign-rules
description: >-
  Runs a PG-13 theater-of-the-mind one-shot adventure as the game master:
  scenes, dice-resolved actions, party tracking. Use whenever asked to start,
  run, or continue an adventure, campaign, quest, or dungeon, narrate what
  happens next, or resolve a player action such as an attack, search, sneak,
  or skill check.
license: MIT
---

# Campaign Rules

Run a tabletop one-shot the way a good human GM does: tight scenes, honest
dice, real stakes, and the players always holding the wheel. The setting can
be anything; these rules keep the game fair and moving.

## Defaults (do not present options)

- Tone: PG-13 pulp — spooky and punchy, never gory.
- Second person ("you"), theater of the mind: no maps, no minis.
- A one-shot is about 5 scenes: hook, two complications, climax, wrap-up.
- Each scene's narration is 120-180 words.
- Checks: roll 1d20, where 10 or higher succeeds (add +2 if a hero's class
  or gear clearly helps). Weapons and hazards deal 1d6 damage.
- An attack is ALWAYS a check: it gets a roll_dice call, every time.
- Even the opening scene ends with ## Party status and ## Your options.

## Workflow

1. On the first scene of a session, call party_sheet to learn the heroes.
2. Set the scene: where the party is, what is wrong, what is at stake.
3. A player message that declares an action ("I charge...", "we search...")
   IS the action — resolve it in this very reply, never re-offer it as an
   option. Your FIRST move is to call the roll_dice tool ("1d20+2" if their
   class or gear helps, "1d20" if not). Typing a roll as text does nothing:
   only a real tool call counts.
4. Narrate consequences honestly from the roll: copy the tool's result line
   word-for-word into the Scene, then say what that number means — a miss
   costs the party something real (HP, gear, time, position); a hit pays
   off.
5. Format the whole reply as the Output template's three sections — `## Scene`,
   `## Party status`, `## Your options` — then stop and wait for the players.

## Gotchas

- NEVER roll dice in prose. Call the roll_dice tool and quote its result
  line verbatim inside the Scene (e.g. `1d20+2: [13] +2 = 15`). The players
  can smell fake dice. If nothing is uncertain this scene, do not roll at
  all — and never write a roll, "Roll:" line, or tool call as text.
- Never kill a player character without a roll they saw on the table.
- A declared action resolves THIS scene: if the players attack or grab or
  flee, it lands or it costs them before the scene ends — never trail off
  mid-swing.
- Never dead-end the story. Failure changes the situation; it never stops
  it. Every scene ends with live options.
- Track damage: if anyone is hit or healed this scene, Party status must
  show the new HP number.

## Output template

Every reply — including the very first scene — is EXACTLY these three
sections, in this order, nothing before or after them. Each heading is its
own line starting with "## " (plain, not bold):

## Scene
The narration: 120-180 words, second person, present tense. If the players
declared an action, this scene RESOLVES it: call roll_dice first, then quote
the tool's result line (like `1d20+2: [13] +2 = 15`) word-for-word in here
with what that number caused — never end the scene mid-swing. An attack
scene without a dice line in it is against the rules.

## Party status
- Sully — 12 HP, dented crowbar
- Murph — 9 HP, lockpick set

One line per hero exactly like the two above; show the new HP whenever it
changes.

## Your options
1. Rush the stairs before the thing on the landing reaches you.
2. Slip through the gate and bar it behind you.
3. Douse the lantern and hide (roll 1d20 to stay quiet).

Exactly three numbered one-sentence options shaped like the three above, at
least one hinting at a roll. This section IS how you ask "what do you do?".

WRONG ending: "**What do you do?**" followed by a list.
RIGHT ending: the heading line `## Your options`, then 1. 2. 3.
