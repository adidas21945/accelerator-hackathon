# skill-forge — the agent that builds skills

> Theme: wildcard · Lane: L1 · Difficulty: 🦞🦞 · Offline: fully · Keys: none

## Pitch

Every team at Agent Build Day ships a skill; this starter makes the first one
a 10-minute job. Answer five questions (or hand it an `answers.json`, or a
one-line task) and the forge drafts a complete SKILL.md with its own
`skill-author` skill — the skill that teaches the model how to write skills —
writes it to disk, and PROVES it by running the agentskills validator plus a
craft lint (trigger-rich description, Defaults/Gotchas/Output-template
sections). If the draft fails, the model gets the validator's exact words for
one repair round. Exit code 0 means a spec-valid skill exists on disk. The
self-referential bit is the point: the forge is built from the very artifact
it produces.

## Quickstart

```bash
# from the repo root — local model by default (see docs/SETUP.md)
uv run python projects/wildcards/skill-forge/agent.py \
  "a skill that formats stand-up updates for Slack"

# the live-demo interview: 5 questions, one validated skill
uv run python projects/wildcards/skill-forge/agent.py

# non-interactive: answers.json in, validated skill directory out
uv run python projects/wildcards/skill-forge/agent.py \
  --answers projects/wildcards/skill-forge/fixtures/answers.json --out /tmp/forge-test
uv run agentskills validate /tmp/forge-test/support-reply   # the proof

# the eval baseline (no skill), and the house evals:
uv run python projects/wildcards/skill-forge/agent.py "..." --no-skill
uv run python -m agentkit.evals projects/wildcards/skill-forge
```

## Demo script (90 seconds)

1. Run the interview, answer with your team's actual hackathon job. Point at
   the `## Validation` section — that's the real validator verdict, not the
   model's opinion — and the footer: the skill is sitting in a directory you
   can `cp -r` straight into your project.
2. Watch stderr: when a draft gets rejected you see the validator's words and
   the repair round fire. Self-correction on a 3B, grounded in a real tool.
3. Run the same task with `--no-skill`: the baseline writes prose about
   skills (or names one "CSV to Data Brief", uppercase and spaces) and the
   validator pipeline fails it. Exit code 1.
4. Open `evals/benchmark.json`: with-skill 3/3 vs without-skill 0/3 on a 3B
   local model (granite4:micro) — delta +1.00, reproduced across two runs.

## Make it yours (extension ideas)

1. **Forge your own skill first** — point it at YOUR project's job ("review
   storm-shelter data briefs", "draft D&D encounters") and install the result.
   That is the event's deliverable, scaffolded in minutes.
2. **Eval-scaffolder mode** — `--with-evals` that also emits an `evals.json`
   (3 cases, ≥3 assertion types) for the generated skill, so every forged
   skill arrives with its own benchmark.
3. **Registry lint** — loop the validator + `craft_lint()` over every
   `skills/*/` in a repo and print a quality table; the forge becomes the
   event's CI gate.
4. **Description-quality grader** — second model pass that adversarially asks
   "would this description route, given these 10 distractor tasks?" and
   scores it; wire it in as a third validation layer.
5. **Frontier comparison** — run the same evals with
   `MODEL_PROVIDER=anthropic` and put the delta table in
   docs/MODEL_SELECTION.md; does a frontier model still need the repair round?

## Rubric mapping

| Criterion (pts) | Where this starter already scores | What you still must do |
|---|---|---|
| Shippability (25) | runs from README, offline, no keys; exit codes mean something; MIT | your public repo + README |
| ADLC (20) | docs/ADLC.md logs 3 real iterations with the eval evidence | re-run the loop on YOUR change |
| Model Selection (20) | local-first rationale + measured numbers; verification routed to code, not models | add your frontier comparison |
| Lane Merit (20) | end-to-end: interview → file on disk → tool-verified, honest +1.00 delta | forge a skill your project actually uses |
| Skill Quality (15) | skill-author validates, trigger-rich description, defaults/gotchas/template; it wrote the skills this repo grades | keep your forged skills passing the lint |
