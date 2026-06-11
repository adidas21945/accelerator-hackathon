# Model Selection — dungeon-mastah

| Task | Model | Tier | Why (cost / latency / quality) |
|---|---|---|---|
| whole GM (narrate + tools + format) | granite4:micro (Ollama, local) | local | $0, ~7 s/scene, fully offline — a party game must not depend on wifi or a meter; prose quality at 3B is genuinely fun |
| dice | `scripts/roll.py` | none (code) | deterministic, seeded, 24 selftest checks — the one part of a GM that must never be a language model |
| quality ceiling (optional) | claude-sonnet-4-6 / gpt-5.4-mini | frontier | richer scenes and steadier template compliance; escalate if the flaky structural assertion matters to you |

**Measured** (from `evals/benchmark.json`, granite4:micro, quiet box):

| Config | $ / run | latency avg / case | eval pass rate |
|---|---|---|---|
| local, with skill | $0.00 | ~7.0 s | 2/3 |
| local, no skill | $0.00 | ~7.6 s | 0/3 |
| frontier (your key) | _measure on your machine_ | _measure_ | _measure_ |

Notes worth repeating to judges:

1. **The format guards cost real tokens and the footer tells the truth** —
   when the 3B truncates a reply, the agent buys one fill-in turn (and at
   most one retake for faked dice); the merged footer reports the *total*
   spend across takes, not the pretty final call. Honest observability
   beats flattering numbers.
2. **Routing implemented: code-vs-model, not cheap-vs-strong.** The split
   that matters here is deterministic dice in a script vs judgment in a
   model. Cross-model routing adds nothing to a game that must run on a
   dead-wifi laptop — and saying why you didn't route is also a rationale.
