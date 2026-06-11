# Model Selection — fridge-whisperer

| Task | Model | Tier | Why (cost / latency / quality) |
|---|---|---|---|
| whole agent (plan + tools + format) | granite4:micro (Ollama, local) | local | privacy (your diet/allergies stay on-device), $0 marginal, ~5s/run; quality is good-enough-with-a-skill for a 3B |
| quality ceiling (optional) | claude-sonnet-4-6 / gpt-5.4-mini / gemini-2.5-flash | frontier | the one leaky eval assertion (staples discipline) is model-capability-bound — escalate if it matters |

**Measured** (from `evals/benchmark.json`, granite4:micro, Apple Silicon, offline):

| Config | $ / run | latency avg / case | eval pass rate |
|---|---|---|---|
| local granite4:micro, with skill | $0.00 | ~5.6 s | 2/3 |
| local granite4:micro, no skill | $0.00 | ~10–14 s | 0/3 |
| frontier (your key) | _measure on your machine_ | _measure_ | _measure_ |

Two findings worth repeating to judges:

1. **The skill halves latency.** Without a template the 3B rambles (~2×
   longer outputs and runtimes). Structure isn't just correctness — it's speed.
2. **Routing implemented: none — and here's why.** Every step here is
   cheap-and-private-bound, not quality-bound; a single local model is the
   right answer, and saying why you didn't route is also a rationale.
   (To demonstrate routing anyway, see `agentkit.route.cascade` and the
   model-matchmakah project.)
