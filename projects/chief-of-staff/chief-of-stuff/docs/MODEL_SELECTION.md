# Model Selection — chief-of-stuff

The flagship claim: **route by task type, decided at design time, recorded
at run time.** Five steps, five routing decisions, and the agent prints the
receipt (the routing table) after every run.

| Task | Model | Tier | Why (cost / latency / quality) |
|---|---|---|---|
| ingest (ics/md/rss parsing) | none — deterministic code | — | parsing must be identical every run; $0, ~0s; the zeroth routing decision is "no model at all" |
| summarizer (per-source digests) | granite4:micro (Ollama, local) | local/cheap | volume-bound AND privacy-bound: touches every private note every morning; compression is template work a 3B does fine |
| prioritizer (rank top-3) | provider's strong model, e.g. claude-opus-4-8 | strong → local fallback | the ONE judgment call — ranking ten todos against four meetings is quality-bound; degrades gracefully to local with no key (and the table says so) |
| researcher (headline relevance) | granite4:micro | local/cheap | cheap yes/no filtering; allowed to return "nothing essential" — never worth frontier tokens |
| render (skill template fill) | granite4:micro | local/default | template-bound, not reasoning-bound; the morning-brief skill carries the structure |

**Measured** (granite4:micro, Apple Silicon, `AGENT_OFFLINE=1`; from
`evals/benchmark.json` and the run's routing table):

| Config | $ / run | latency avg / case | eval pass rate |
|---|---|---|---|
| all-local (strong→local fallback), with skill | $0.00 | 52.5 s (4 model calls) | 3/3 |
| all-local, no skill on the final render | $0.00 | 40.6 s | 0/3 |
| frontier prioritizer (`ANTHROPIC_API_KEY` set) | _measure on your machine_ | _measure_ | _measure_ |

One real brief, per-agent (verbatim routing table, offline run):

```
agent       model           route                               tok (p+c)         $      s
ingest      (code)          deterministic                             0+0    0.0000    0.0
summarizer  granite4:micro  local/cheap                           723+136    0.0000    5.3
prioritizer granite4:micro  strong→local fallback (offline)       531+113    0.0000    2.2
researcher  granite4:micro  local/cheap                            394+70    0.0000    5.1
render      granite4:micro  local/default                        1337+363    0.0000    5.1
TOTAL                                                            2985+682    0.0000   17.7
```

Findings worth repeating to judges:

1. **~80% of the tokens never need a frontier model.** Only the prioritizer
   (531+113 of 2985+682 tokens, ~18% of the run) is quality-bound. Routing
   the other four steps local makes the marginal brief cost $0.00 — and the
   private meeting notes never leave the machine.
2. **The fallback is measured, not hypothetical.** The local prioritizer's
   known gap: it ranked "pull Q2 stats" above the deadline-bound "send the
   revised proposal before the 09:00 sync" in 2 of 3 observed runs. That is
   precisely the call a strong model is for; the fix is one env var
   (`export ANTHROPIC_API_KEY=...`) and the routing table row flips from
   `strong→local fallback (no key)` to `anthropic/strong`.
3. **Latency under contention is real data.** The same 4-call brief
   measured 17.7s on a quiet box and 66.1s while Ollama queued other jobs
   (eval cases ranged 11–81s); single-call prep runs took ~3s. Measure on
   your machine before quoting demo timings.

Routing implemented: **static per-task** (the hub knows at design time which
step is judgment). Rejected: `agentkit.route.cascade` — its self-grading
call costs a second model call on every query to discover what this
architecture already knows; rejected all-frontier because 4 of 5 steps are
template-bound and the data is private. Saying why you didn't route
dynamically is also a rationale.
