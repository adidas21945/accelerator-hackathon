# ADLC Worksheet — skill-forge

## 1. Scope
A hackathon team describes a job in plain language; the forge returns a
spec-valid skill directory on disk, proven by the agentskills validator, in
one command. One end-to-end success case: the bike-shop `answers.json` →
`/tmp/forge-test/support-reply` validating with exit 0. Out of scope:
multi-skill packs, eval scaffolding (extension #2), registry-wide linting.

## 2. Design
One agent, zero tools (a 3B fumbles long-string tool args; the validator
runs harness-side instead), one skill (`skill-author`) carrying the spec +
the authoring craft. The loop: run_agent → extract the fenced SKILL.md →
write `<out>/<name>/SKILL.md` → subprocess the validator → on failure, ONE
repair round with the validator's stderr in the prompt. Verification is
code, generation is model — see docs/MODEL_SELECTION.md.

## 3. Build
agentkit loop + ~200 LOC of harness. Validator invocation that survived
testing: `[sys.executable, "-m", "skills_ref.cli", "validate", dir]` — the
venv python always has `skills_ref`, no PATH or cwd assumptions (the
`agentskills` console script is the same entry point).

## 4. Evaluate  ← the loop ran 3 times; this log is the point
3 cases × with/without skill; the `script` assertion
(`evals/check_generated.py`) re-extracts the SKILL.md, re-validates it in a
temp dir, and statically checks the craft rules. Iteration log:
- **v1 bug:** the model copied the job text verbatim into `description:`
  and dropped the trigger clause — perfect body, unroutable skill. Fix:
  the output-template preamble (the highest-attention zone, per the pilot)
  now demands the literal words "Use whenever"; rejected otherwise.
- **v2 bug:** first full eval 2/3 — the data-brief body silently lost its
  `## Defaults` section, and no repair fired because the spec validator
  only reads frontmatter. Fix, both levers: the skill names the five body
  parts as rejection criteria, and `craft_lint()` moved those rules from
  model willpower into harness code so the repair round triggers on them.
- **v3:** 3/3 with skill, 0/3 without, delta +1.00 — reproduced on a second
  full run (one with-skill draft needed the craft-lint repair; every
  baseline burned its repair round and still failed).
- **Eval-engineering lesson:** asserting `(?i)passed|valid` inside the
  Validation section is vacuous — the section grabber includes the heading
  line, and "Validation" contains "valid". We assert the validator's
  literal verdict line `^valid skill:` instead. Assert outcomes, not echoes.

## 5. Deploy
README quickstart; fully offline, zero keys; the artifact is a directory
you `cp -r` into your project. Exit code 0 ⇔ the validator passed, so the
forge slots into CI as-is.

## 6. Observe
The run footer prints turns / tokens / $ / latency / the skill's directory;
every rejected draft logs the verdict that triggered the repair to stderr.
What the traces taught us: baselines reliably fail to fence the file (3/3
"no fenced SKILL.md block" in run A), and when coached into fencing by the
repair prompt they still miss the spec ("CSV to Data Brief" as a name) —
the delta is knowledge, not formatting luck.

## 7. Iterate
Next loop, in order: (1) `--with-evals` so every forged skill ships its own
evals.json; (2) registry-lint mode over all `skills/*/` in the repo;
(3) frontier-model comparison — does claude-sonnet ever need the repair
round?; (4) adversarial description grader (would this route against 10
distractor tasks?).
