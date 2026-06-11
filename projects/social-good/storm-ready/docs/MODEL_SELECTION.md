# Model Selection — storm-ready

| Task | Model | Tier | Why (cost / latency / quality) |
|---|---|---|---|
| whole agent (fetch alerts + forecast, format brief) | granite4:micro (Ollama, local) | local | offline-resilience-bound: an emergency-prep tool must keep working when the grid and wifi are sad — local + fixtures means it always answers; $0 marginal; the task is template-bound (the skill carries the judgment), well inside a 3B with a skill |
| quality ceiling (optional) | claude-sonnet-4-6 / gpt-5.4-mini / gemini-2.5-flash | frontier | quality-bound bits — digesting a 6-alert live feed gracefully, multilingual briefs — escalate if you ship those |

**Measured** (from `evals/benchmark.json` and run footers; granite4:micro,
Apple Silicon, offline fixtures unless noted):

| Config | $ / run | latency avg / case | eval pass rate |
|---|---|---|---|
| local granite4:micro, with skill | $0.00 | 36.7–54.8 s (two runs; load-dependent) | 3/3, twice |
| local granite4:micro, no skill | $0.00 | 41.7–61.9 s | 0/3, twice |
| local, live NWS (demo run, 6 real alerts) | $0.00 | ~54.8 s | n/a (live is for demos, fixtures for measurement) |
| frontier (your key) | _measure on your machine_ | _measure_ | _measure_ |

Findings worth repeating to judges:

1. **The skill is both the correctness and the speed.** With the template,
   3/3 in both eval runs; without it, 0/3 — and the no-skill runs were
   ~14% slower in both runs (unstructured 3Bs ramble longer for a worse
   answer).
2. **Local is a requirement here, not a compromise.** The user story is "the
   forecast says hurricane and the power flickers" — a tool that needs a
   cloud key fails exactly when it matters. Fixtures + local model keep the
   demo (and the household) functional with zero connectivity.
3. **Routing implemented: none — and here's why.** Every step is
   availability- and cost-bound, not quality-bound; one local model is the
   right answer. The named escalation (extension #5 in the README) is
   severity-based: quiet days local, Extreme-severity days
   `agentkit.route.cascade` to a frontier model.
