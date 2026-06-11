# Model Selection — wicked-smaht-bahtendah

| Task | Model | Tier | Why (cost / latency / quality) |
|---|---|---|---|
| whole agent (lookup + adapt + format) | granite4:micro (Ollama, local) | local | $0 marginal, ~4–11 s/run quiet-box; the job is template-bound adaptation of a fetched recipe, not open-ended reasoning — skill-carried rules close the gap |
| quality ceiling (optional) | claude-sonnet-4-6 / gpt-5.4-mini / gemini-2.5-flash | frontier | the residual risk (stochastic classic selection, copying fixture extras the user lacks) is capability-bound — escalate if your demo can't tolerate a re-roll |

**Measured** (from `evals/benchmark.json`, granite4:micro, Apple Silicon, offline):

| Config | $ / run | latency avg / case | eval pass rate |
|---|---|---|---|
| local granite4:micro, with skill | $0.00 | ~4.4 s | 3/3 |
| local granite4:micro, no skill | $0.00 | ~5.3 s | 0/3 |
| frontier (your key) | _measure on your machine_ | _measure_ | _measure_ |

Latency honesty: on a busy Ollama queue (event conditions!) the same suite
averaged 23–38 s/case; the committed quiet-box run averaged 4–5 s. Pass
rates were identical under both — budget demo time, not demo quality. A
clean live margarita run is 2 turns, ~2.5K+0.3K tokens, ~4.3 s.

Findings worth repeating to judges:

1. **The defaults beat is skill-bound, not model-bound.** Without the skill
   the 3B never zero-proofs and never sections (0/3); with it, 3/3 at $0.
   You don't need a frontier model to enforce a policy — you need the policy
   written where the model can't miss it.
2. **The live API made the agent worse, and the fixture made it better.**
   TheCocktailDB's keyless test tier truncates `filter.php` to ONE result
   ("lime" → just "After Dinner Cocktail"), which sent the 3B on a
   wild-goose chase; the 11-classic fixture cabinet gives richer discovery
   than live. `search.php` (lookup by name) is full-fat live — so the skill
   routes named classics straight to it.
3. **Routing implemented: none — and here's why.** Every step is
   cheap-and-template-bound; a single local model is the right answer, and
   the fix for every failure we hit was skill text or tool shape, never
   model size. (To demonstrate routing anyway, see `agentkit.route.cascade`
   and the model-matchmakah project.)
