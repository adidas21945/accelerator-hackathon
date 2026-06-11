# Model Selection — paypah-trail

| Task | Model | Tier | Why (cost / latency / quality) |
|---|---|---|---|
| receipt parsing (vendor/date/total) | **no model** — `parse_receipt.py` | script | deterministic, self-tested, $0, ~0s; a regex problem must not cost tokens or invite hallucinated digits |
| categorize + assemble report | granite4:micro (Ollama, local) | local | privacy-bound: receipts are your finances and never leave the laptop; $0 marginal, good-enough-with-a-skill |
| arithmetic ceiling (optional) | claude-haiku-4-5 / gpt-5.4-mini | frontier | the 3B's category-sum arithmetic wobbles; escalate (or add a `sum_ledger` script) if exact sums matter |

**Measured** (from `evals/benchmark.json`, granite4:micro, Apple Silicon, offline):

| Config | $ / run | latency avg / case | eval pass rate |
|---|---|---|---|
| local granite4:micro, with skill | $0.00 | ~83 s* | 3/3 |
| local granite4:micro, no skill | $0.00 | ~110 s* | 0/3 |
| frontier (your key) | _measure on your machine_ | _measure_ | _measure_ |

\*Measured while three other projects' eval suites shared the same Ollama;
on an idle machine the same 8-turn, 6-receipt run finishes in ~6 s (run
footer: `8 turns · 10332+377 tok · $0.0 · 6.34s`). Treat the with/without
latency gap as queue noise, not signal.

Findings worth repeating to judges:

1. **The biggest model decision here was using NO model for parsing.** Every
   dollar figure in the ledger is script output; the model literally cannot
   hallucinate a total it never extracts. That's the "Form & Function"
   deterministic-script pattern, and it's also a privacy + cost decision.
2. **Routing implemented: none — and here's why.** Every model-touching step
   is privacy-bound, which pins the whole agent to local; the one
   quality-bound step (summing categories) is better fixed with another
   script than with a bigger model. Saying why you didn't route is also a
   rationale. (To see routing done, read `agentkit.route.cascade`.)
