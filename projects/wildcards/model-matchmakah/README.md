# model-matchmakah — the cascade router you can feel

> Theme: wildcard · Lane: L1 · Difficulty: 🦞🦞 · Offline: partial (cascade runs local-only; real escalation needs a frontier key) · Keys: optional frontier

## Pitch

Every query goes cheap-first: the local 3B answers, grades its own confidence,
and escalates to a frontier model only when it's unsure — then shows you the
receipt: models tried, confidence, dollars, seconds. The `routing-rationale`
skill turns raw cascade facts into the exact evidence format the Model
Selection rubric line (20 pts) wants to see, and `agentkit.route.cascade` is
one import away from doing the same in any other starter. This project IS the
demo for that module.

## Quickstart

```bash
# from the repo root — local model by default (see docs/SETUP.md)
uv run python projects/wildcards/model-matchmakah/agent.py \
  "What is the capital of Massachusetts?"

# the whole economics story in one table: 5 canned tasks, routed
uv run python projects/wildcards/model-matchmakah/agent.py --batch
uv run python projects/wildcards/model-matchmakah/agent.py --batch --threshold 0.99

# baseline (no receipt), offline, and the house evals:
uv run python projects/wildcards/model-matchmakah/agent.py "..." --no-skill
uv run python projects/wildcards/model-matchmakah/agent.py "..." --offline
uv run python -m agentkit.evals projects/wildcards/model-matchmakah
```

**With a frontier key** the strong tier becomes real: `export
MODEL_PROVIDER=anthropic ANTHROPIC_API_KEY=sk-...` and escalated rows read
`granite4:micro -> claude-opus-4-8` with a non-zero cost column. Without a
key the agent degrades gracefully — the receipt reads "escalation unavailable
— no frontier key; staying local" instead of stack-tracing. Two-tier local
also works: `export AGENTKIT_STRONG_MODEL=llama3.1:latest` (any Ollama model
you've pulled).

## Demo script (90 seconds)

1. Run the quickstart question. Read the receipt out loud: resolved locally,
   confidence 1.00, $0.0000 — and the "What it means" line says what a
   frontier-only setup would have paid for the same answer.
2. Run `--batch`: 5 tasks, one table — route, confidence, cost, latency,
   "resolved locally: 5/5". That table is your MODEL_SELECTION.md evidence.
3. Run `--batch --threshold 0.99`: 4/5 now escalate and total latency ~2×.
   The knob is economics, not truth — and a 3B grades itself 0.90–1.00, so
   the useful band sits high (see docs/MODEL_SELECTION.md).
4. `--no-skill`: same router, no receipt — that difference is the skill, and
   it's the whole +1.00 eval delta in evals/benchmark.json.

## Make it yours (extension ideas)

1. **Plug it into another starter** — one line in fridge-whisperer (or any
   project): replace a `llm.chat(...)` with `route.cascade(...)` and put the
   `table_row` in your docs. Instant measured Model Selection evidence.
2. **Learned routing** — replace `self_grade` with a RouteLLM-style
   classifier: a tiny prompt (or logistic regression over task features) that
   predicts escalate/stay *before* answering, saving the grading call.
3. **Per-task static routing table** — some task types should never cascade
   (haiku → local, contracts → frontier). A dict of regex → (provider, tier)
   in front of the cascade is 10 lines and demos beautifully next to it.
4. **OpenRouter as the strong tier** — point `LOCAL_BASE_URL`-style env at
   OpenRouter and make the strong tier any model on the menu; compare three
   frontier models' cost/quality on the same batch.
5. **Calibrate the grader** — log (confidence, actually-correct) pairs from
   the batch, plot them, and pick the threshold where the curves cross
   instead of guessing.

## Rubric mapping

| Criterion (pts) | Where this starter already scores | What you still must do |
|---|---|---|
| Shippability (25) | runs from README; MIT; `agentskills validate` passes; degrades gracefully without keys | your public repo + README |
| ADLC (20) | docs/ADLC.md logs a real evaluate→iterate loop (the 0.90 confidence-floor find) | re-run the loop on YOUR change |
| Model Selection (20) | this project IS the demo: measured batch tables, threshold sweep, hypothetical frontier costs in docs/MODEL_SELECTION.md | add a real frontier run with your key |
| Lane Merit (20) | end-to-end router + receipt on realistic queries, honest about a 3B's self-grading | your twist |
| Skill Quality (15) | triggers, defaults, gotchas with measured numbers, strict output template, +1.00 delta | keep the delta positive |
