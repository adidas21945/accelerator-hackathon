# Model Selection — qrious-citizen

| Task | Model | Tier | Why (cost / latency / quality) |
|---|---|---|---|
| whole agent (discover → pull → brief) | granite4:micro (Ollama, local) | local | the data is public and the API is keyless, so the bind is cost/latency, not privacy; $0 marginal and ~7 s/run idle. Quality is viable ONLY because counting lives in the tools — the model copies tallies, it never computes them |
| quality ceiling (optional) | claude-sonnet-4-6 / gpt-5.4-mini / gemini-2.5-flash | frontier | multi-dataset judgment calls (which of 3 candidate datasets actually answers the question) and tighter tool-arg discipline — escalate if you add ambiguous datasets |

**Measured** (from `evals/benchmark.json` and run footers, granite4:micro,
Apple Silicon, offline fixtures):

| Config | $ / run | latency avg / case | eval pass rate |
|---|---|---|---|
| local granite4:micro, with skill | $0.00 | 42.3 s contended† / ~7 s idle | 3/3 |
| local granite4:micro, no skill | $0.00 | 33.8 s contended† / ~10 s idle | 0/3 |
| local, live data.boston.gov (not evals) | $0.00 | ~16 s (4 turns, 7.2k tok) | n/a |
| frontier (your key) | _measure on your machine_ | _measure_ | _measure_ |

† benchmark numbers were measured while the shared Ollama box was busy with
other builds; the idle figures are from solo runs of the same cases.

Findings worth repeating to judges:

1. **Move the math, keep the model.** v0 of `get_records` was going to return
   raw JSON rows; a 3B cannot count 42 rows by neighborhood, let alone 5,000.
   The tool returns deterministic tallies instead, and the 3B's only jobs are
   tool choice and prose — that one design call is why local-only scores 3/3.
2. **Tool docstrings outrank skill prose.** The model ignored the skill's
   "filter by topic" instruction but obeyed the same rule moved into
   `get_records`' docstring ("you MUST set where..."). The schema the model
   sees on every turn is the highest-attention prompt real estate.
3. **Routing implemented: none — and here's why.** Every run is
   cheap-and-template-bound: discovery is one keyless GET, counting is code,
   prose is templated by the skill. Nothing here is quality-bound until you
   add ambiguous multi-dataset questions (see the frontier row). To
   demonstrate routing anyway, see `agentkit.route.cascade`.
