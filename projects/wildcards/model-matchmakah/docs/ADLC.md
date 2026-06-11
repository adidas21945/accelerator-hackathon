# ADLC Worksheet — model-matchmakah

## 1. Scope
A builder asks anything; the agent answers cheap-first and shows the
routing receipt (models tried, confidence, $, latency). One end-to-end
success case: "What is the capital of Massachusetts?" → correct answer +
faithful receipt, resolved locally at $0.0000. Out of scope: multi-turn
sessions, tool use, learned routing, real cost accounting beyond the
PRICES table.

## 2. Design
One cascade (`agentkit.route.cascade`, not reimplemented) + one formatting
call + one skill that defines the receipt format. Cheap tier pinned to
local granite4:micro (answer, grade, format are all cheap/template-bound);
strong tier follows `$MODEL_PROVIDER` so a key upgrades it to a real
frontier hop. Graceful degradation designed in up front: pre-flight
`llm.resolve(None, "strong")` instead of catching mid-cascade, so an
unavailable strong tier costs zero wasted local calls — the degraded path
re-runs `cascade` with threshold 0.0, which can never trip (confidence is
clamped to ≥ 0). See docs/MODEL_SELECTION.md.

## 3. Build
~184 LOC agent + 96-line skill, agentkit only, no new deps. The facts
block hands the formatter pre-formatted values ("$0.0000", "0.95 (met
threshold 0.7)") — a lesson lifted from the fridge-whisperer pilot: put
the exact strings you want in the model's highest-attention zone instead
of trusting a 3B to format numbers.

## 4. Evaluate  ← the loop ran 3 times; this log is the point
3 cases × with/without skill (`evals/evals.json`). Iteration log:
- **v1:** first live run worked and the receipt numbers were verbatim-
  faithful. Evals 3/3 with skill, 0/3 without (delta +1.00).
- **v2 bug (found by testing the README's own claim):** with
  `AGENTKIT_STRONG_MODEL=llama3.1:latest`, the escalated receipt said
  "strong tier = same local model" (the code checked *provider*, not
  *model id*) and the 3B narrated "0.95 cleared the threshold of 0.99" —
  backwards. Two fixes: compare model ids in the outcome string, and give
  the skill one example sentence per routing outcome (resolved locally /
  escalated / escalation unavailable) — a single example had biased the
  formatter into narrating every receipt as "resolved locally". Re-tested:
  narration correct.
- **v3 measured finding:** granite4:micro self-grades 0.90–1.00 on
  everything (haiku and Monty Hall included), so the default 0.7 threshold
  never escalates and 0.3 vs 0.9 are the same router. Changed: `--threshold`
  help now names the working band (try 0.3 vs 0.99), and the skill's gotcha
  quotes the measured floor. Kept 0.7 as the default on purpose — it is the
  honest "textbook setting", and discovering it does nothing here is the
  demo.
- **Final:** with-skill 3/3, without-skill 0/3, delta +1.00.

## 5. Deploy
README quickstart; runs offline with zero keys (`--offline` hard-disables
escalation); without a key but with `MODEL_PROVIDER=anthropic` it degrades
to "escalation unavailable — no frontier key; staying local" instead of a
stack trace. Nothing to configure beyond `ollama pull granite4:micro`.

## 6. Observe  ←
Every run footers the outcome, route, confidence, $, and total latency;
`--batch` aggregates the same via `RouteResult.table_row`. Two things the
traces taught us: (1) latency is Ollama-load-bound, not routing-bound —
the same 5-task batch cost 106.2 s cold and 7.3 s warm; (2) the grading
call's real price is *input* tokens (68–388 measured — it re-reads the
whole answer), not its ~9 output tokens.

## 7. Iterate
Next loop, in order: (1) calibrate the grader — log (confidence, correct?)
pairs from the batch and pick the threshold where the curves cross instead
of folklore 0.7; (2) a real frontier run of the same batch with a key,
replacing the hypothetical table in MODEL_SELECTION.md; (3) skip-the-grade
mode: a pre-answer difficulty classifier (RouteLLM-style) to save the
second local call on obviously easy queries.
