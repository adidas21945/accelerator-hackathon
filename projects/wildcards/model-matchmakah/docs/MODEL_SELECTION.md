# Model Selection — model-matchmakah

This project IS the Model Selection demo: the router's receipt is the
rubric evidence. Every number below is from real runs on this repo's
default stack (granite4:micro via Ollama, Apple Silicon) unless a table is
explicitly marked **hypothetical**.

## Who does what

| Task | Model | Tier | Why (cost / latency / quality) |
|---|---|---|---|
| answer attempt (every query) | granite4:micro (Ollama, local) | cheap | $0 marginal, private, fast when warm; good enough for most of the batch |
| self-grade (every query) | granite4:micro | cheap | a second local call; its price is input tokens (it re-reads task + answer: 68–388 prompt tok measured) |
| receipt formatting | granite4:micro | cheap | template-bound work, exactly what a 3B + a strict skill does well |
| escalation target (only when confidence < threshold) | `$MODEL_PROVIDER` strong tier (e.g. claude-opus-4-8) | strong | quality-bound queries only — that's the whole cascade bet |

Routing implemented: **cascade (`agentkit.route.cascade`)** — cheap first,
self-grade, escalate under the threshold. Rejected: a static per-task
routing table — it can't catch "easy-looking question the small model
flubs", which is the case routing exists for (it's extension idea #3 in the
README if you want both).

## Measured: the --batch table (local-only, threshold 0.7, model warm)

```
task                                                           route                               conf   cost $    sec
What is the capital of Massachusetts?                          granite4:micro                      1.00   0.0000    0.6
Explain why switching doors wins the Monty Hall problem, con…  granite4:micro                      0.95   0.0000    3.3
A T pass costs $90/month and a single ride costs $2.40. How …  granite4:micro                      1.00   0.0000    2.1
Write a haiku about the Boston T in winter.                    granite4:micro                      0.95   0.0000    0.6
Draft a 3-bullet incident update from these facts: API error…  granite4:micro                      0.90   0.0000    0.7
TOTAL                                                                                                     0.0000    7.3
resolved locally: 5/5 · escalations: 0
```

Cold-start caveat (measured): the first batch after `ollama serve` took
106.2 s for the same 5 tasks — Ollama model load dominates, not routing.

## Measured: the threshold sweep (same 5 tasks)

| `--threshold` | escalations | total $ | total latency | what happened |
|---|---|---|---|---|
| 0.3 | 0/5 | $0.0000 | 7.7 s | identical to 0.7 — nothing grades below 0.9 |
| 0.7 (default) | 0/5 | $0.0000 | 7.3–106.2 s (warm–cold) | all local |
| 0.99 | 4/5 | $0.0000 | 197.4 s | every escalation re-ran locally (no frontier configured), ~2× latency for $0 |

**The finding that matters:** granite4:micro self-grades 0.90–1.00 on
*everything* — Monty Hall, arithmetic, haiku alike (confidence floor 0.90
across all runs). So for this grader the threshold knob only works in the
0.92–0.99 band; 0.3 vs 0.7 vs 0.9 are all the same router. Thresholds are
economics, not truth — and they must be calibrated to the confidence
distribution your grader actually emits, not to a textbook 0.7.

## Hypothetical: the same batch with a frontier key

**Marked hypothetical:** no frontier key exists in this environment. Costs
below are computed from the *measured* local token counts (answer calls:
236 prompt + 615 completion tokens across the batch) × the published
$/1M-token PRICES in `agentkit/llm.py` (claude-sonnet-4-6: $3/$15,
claude-opus-4-8: $5/$25, claude-haiku-4-5: $1/$5). Frontier completion
lengths would differ somewhat in practice.

| Setup | est. $ for this 5-task batch | notes |
|---|---|---|
| cascade @ 0.7 (measured) | **$0.0000** | 5/5 resolved locally |
| frontier-only, claude-haiku-4-5 | $0.0033 | per task: .0001 / .0013 / .0016 / .0002 / .0002 |
| frontier-only, claude-sonnet-4-6 | $0.0099 | per task: .0002 / .0039 / .0047 / .0005 / .0007 |
| frontier-only, claude-opus-4-8 | $0.0166 | the receipt's "what you didn't pay" line |
| cascade @ 0.99 with `MODEL_PROVIDER=anthropic` | ~$0.0162 | 4/5 escalate to opus — at 0.99 you pay ~98% of frontier-only; the knob IS the budget |

With a key, an escalated row in the receipt reads
`granite4:micro -> claude-opus-4-8` with a non-zero cost cell; without one,
the agent records "escalation unavailable — no frontier key; staying local"
instead of raising. (Verified live with a second local model standing in as
the strong tier: `AGENTKIT_STRONG_MODEL=llama3.1:latest` produced
`granite4:micro -> llama3.1:latest` receipts.)

## Measured: what the skill costs and buys

From `evals/benchmark.json` (3 cases, with/without skill, offline, warm):

| Config | $ / run | avg latency / case | eval pass rate |
|---|---|---|---|
| cascade + routing-rationale skill | $0.00 | 5.41 s | 3/3 |
| cascade, no skill (raw answer) | $0.00 | 1.83 s | 0/3 |

The formatting pass is one more local call (~3.6 s warm) and is the entire
+1.00 delta: same router, but only the skill turns it into auditable
evidence. The grading overhead is real too — ~9 completion tokens per
grade, but 68–388 prompt tokens because the grader re-reads the answer:
cascading is two local calls before any escalation, and that is the price
of the pattern.
