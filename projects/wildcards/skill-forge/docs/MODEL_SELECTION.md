# Model Selection — skill-forge

| Task | Model | Tier | Why (cost / latency / quality) |
|---|---|---|---|
| draft + repair the SKILL.md | granite4:micro (Ollama, local) | local | template-bound generation with a worked skeleton in the skill; $0, ~10-20 s/draft; private and offline for a room full of laptops |
| verify the draft | **no model** — `skills_ref` validator + `craft_lint()` (subprocess/code) | n/a | verification is deterministic; a 3B "looks valid to me" is worthless next to a real exit code |
| quality ceiling (optional) | claude-sonnet-4-6 / gpt-5.4-mini / gemini-2.5-flash | frontier | richer Gotchas for niche domains; switch with `MODEL_PROVIDER=anthropic` — the validate/repair harness is model-agnostic |

**Measured** (from `evals/benchmark.json`, granite4:micro, Apple Silicon,
offline; two consecutive full runs):

| Config | $ / run | latency avg / case | eval pass rate |
|---|---|---|---|
| local granite4:micro, with skill | $0.00 | 14.9 s / 20.1 s (runs A/B) | 3/3 both runs |
| local granite4:micro, no skill | $0.00 | 39.0 s / 47.6 s | 0/3 both runs |
| frontier (your key) | _measure on your machine_ | _measure_ | _measure_ |

Three findings worth repeating to judges:

1. **Route verification away from models entirely.** The forge's only
   trustworthy component is the cheapest one: a subprocess running the
   agentskills validator. The model proposes; the tool disposes. The repair
   round is the model reacting to the tool's words, not to its own vibes.
2. **Grounded self-repair beats a bigger model here.** In run B, 1 of 3
   with-skill drafts failed the craft lint (dropped "Use whenever") and the
   repair round fixed it — pass rate stayed 3/3 at $0. The baseline gets the
   exact same repair round and still goes 0/3: feedback only helps a model
   that has the rules in context.
3. **The skill more than halves latency** (replicating the pilot's finding):
   15-20 s with the skill vs 39-48 s without. The skeleton stops the 3B from
   rambling essays about what skills are. Structure is speed.
