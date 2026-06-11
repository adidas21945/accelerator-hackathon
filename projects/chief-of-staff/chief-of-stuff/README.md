# chief-of-stuff — the morning-brief orchestrator

> Theme: chief-of-staff · Lane: L3 · Difficulty: 🦞🦞🦞 · Offline: fully (all-local mode) · Keys: optional (frontier + Tavily upgrade paths)

## Pitch

A `briefcase/` folder holds your working life — calendar, todos, meeting
notes, news feeds. A hub agent delegates to three specialists and assembles
the one page you actually need at 7am: top-3 priorities with receipts,
today's schedule, prep for each meeting, and only-if-relevant reading. This
is [BriefingClaw](https://github.com/holzerjm/GACEP-Spring-2026-demo)'s
hub-and-spoke architecture at starter scale — same shape, but BriefingClaw
runs 8 agents on Granite-8B for Lane 2; fork IT for Lane 2, fork THIS for
Lane 3.

The Lane-3 mechanics are deliberately boring: **delegation is explicit
function calls** — `run_brief()` in `agents/orchestrator.py` calls ingest
(deterministic code), then summarizer → prioritizer → researcher, then one
final render through the `morning-brief` skill, and you can read the whole
mechanism in twenty lines. No graph framework, no message bus. Every model
call comes back as an agentkit `ChatResult`, and the hub folds them into a
per-agent **routing table** (model, route, tokens, $, latency) printed after
every run.

## Architecture

```
                       ┌─────────────────────────────┐
 "brief for 6/26" ────▶│   orchestrator (the hub)    │────▶ morning brief
 "prep: client sync"   │   plain function calls      │      + routing table
                       └──┬──────┬─────────┬──────┬──┘
                          │      │         │      │
                ┌─────────▼──┐ ┌─▼────────┐ ┌─────▼──────┐ ┌──▼─────────┐
                │ ingest     │ │summarizer│ │prioritizer │ │ researcher │
                │ code, $0   │ │ local /  │ │ STRONG tier│ │ local /    │
                │ ics·md·rss │ │ cheap    │ │ ↘local f/b │ │ cheap      │
                └────────────┘ └──────────┘ └────────────┘ └────────────┘
                          ... then ONE final local render through
                          skills/morning-brief (or skills/meeting-prep)
```

The teaching split: **ingestion is code, judgment is models.** Parsing
calendar.ics/todos.md/RSS is deterministic (`agents/ingest.py`, zero
tokens); ranking priorities is the one judgment call, so it alone asks for
the "strong" tier — and degrades gracefully to local when no frontier key
is set, with the routing table saying so out loud.

## Quickstart

```bash
# from the repo root — fully offline, all-local (granite4:micro via Ollama)
uv run python projects/chief-of-staff/chief-of-stuff/agent.py \
  "Build my morning brief for Friday, June 26, 2026." --offline

# the second skill — a one-pager for one meeting (composition story):
uv run python projects/chief-of-staff/chief-of-stuff/agent.py \
  --prep "Client sync — Beacon Hill Bikes" --offline

# the eval baseline (no skill on the final render), and the house evals:
uv run python projects/chief-of-staff/chief-of-stuff/agent.py "..." --no-skill
uv run python -m agentkit.evals projects/chief-of-staff/chief-of-stuff
```

A real run prints the brief to stdout and this to stderr (verbatim, local
fallback active because the run was offline):

```
agent       model           route                               tok (p+c)         $      s
ingest      (code)          deterministic                             0+0    0.0000    0.0
summarizer  granite4:micro  local/cheap                           723+136    0.0000    5.3
prioritizer granite4:micro  strong→local fallback (offline)       531+113    0.0000    2.2
researcher  granite4:micro  local/cheap                            394+70    0.0000    5.1
render      granite4:micro  local/default                        1337+363    0.0000    5.1
TOTAL                                                            2985+682    0.0000   17.7
```

## Demo script (90 seconds)

1. Open `briefcase/` — a calendar, todos, meeting notes, a cached feed.
   Point at the trap: a todo, the 09:00 client sync, and a note deadline
   that only compose into priority #1 if the agents cross-reference.
2. Run the quickstart brief. Walk the routing table: four model calls, one
   deterministic ingest, $0.0000, and the prioritizer row admitting
   "strong→local fallback" — with `ANTHROPIC_API_KEY` exported, that same
   row reads `anthropic/strong` with real dollars.
3. Run `--prep "Client sync — Beacon Hill Bikes"` — skill #2, one call,
   ~3s: open questions from the last note lead the page.
4. Show `evals/benchmark.json`: with-skill 3/3 vs without-skill 0/3 on the
   same specialists — the skill template is the entire difference.

## Make it yours (extension ideas)

1. **Live research** — `export TAVILY_API_KEY=...` and the researcher
   searches live instead of reading `feeds/cached-headlines.xml` (any
   failure falls back to the fixture automatically).
2. **Real strong tier** — `export ANTHROPIC_API_KEY=...` (that one env var
   is the whole upgrade) and the prioritizer routes to the strong frontier
   model while everything else stays local. Put the before/after Top-3 in
   your MODEL_SELECTION.md.
3. **Your actual life** — swap `briefcase/` for your notes directory; the
   loaders only assume an .ics, a todos.md, and a folder of dated .md notes.
4. **A fourth specialist** — an email-digest agent via an IMAP/MCP bridge,
   one more row in the routing table; the hub pattern makes it a 10-line
   addition to `run_brief()`.
5. **Scheduled 7am delivery** — wire `deploy/zeroclaw/` (single-binary,
   deny-by-default runtime + cron) or `deploy/openclaw/` (drop the skills
   into a personal agent gateway; read the security caveat first).

## Rubric mapping

| Criterion (pts) | Where this starter already scores | What you still must do |
|---|---|---|
| Shippability (25) | runs offline from README; MIT; both skills pass `agentskills validate` | your public repo + README |
| ADLC (20) | docs/ADLC.md logs 3 real iterations with eval evidence | re-run the loop on YOUR change |
| Model Selection (20) | per-agent routing table with measured tokens/$/latency; graceful strong→local fallback; docs/MODEL_SELECTION.md | add your frontier numbers |
| Lane Merit (20) | 4 cooperating agents + hub, 2 skills, explicit function-call delegation you can read in 20 lines | your twist (4th specialist?) |
| Skill Quality (15) | both skills: triggers, defaults, gotchas, exact output templates; +1.00 eval delta | keep the delta positive |
