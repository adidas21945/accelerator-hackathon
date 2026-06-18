# Contributing — add your own starter

This repo is a **GitHub template** (click *Use this template*) and a set of
worked examples that all follow one shape. Adding your own starter — for Build
Day or after — means copying that shape. Here it is.

## Anatomy of a project

```
projects/<theme>/<name>/
├── agent.py            # the entry point + the run() contract
├── skills/<skill>/SKILL.md   # one validated skill (+ optional scripts/ references/ assets/)
├── evals/evals.json    # the house eval method (with vs without skill)
├── fixtures/           # offline fallback for every networked tool
└── docs/MODEL_SELECTION.md + docs/ADLC.md
```

The gentlest reference is [`fridge-whisperer`](projects/everyday/fridge-whisperer/)
(no network, ~80 lines). Copy it and rename.

## The one contract

Every `agent.py` exposes:

```python
def run(task: str, skill=DEFAULT_SKILL): ...   # returns an AgentResult (or anything with .text)
```

`skill=None` is the **without-skill baseline** — the same code path, no second
branch. That's what the eval runner toggles. Every `agent.py` also starts with
the self-locating bootstrap so `python agent.py "..."` works from anywhere:

```python
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "agentkit").is_dir())))
from agentkit import run_agent, tool
```

## The harness (`agentkit/`)

```python
from agentkit import run_agent, tool, chat, load_skill, cascade

@tool                       # schema comes from the signature + docstring (the docstring is a prompt)
def get_thing(query: str):
    """What it does, and WHEN to use it."""
    return f"sentence-shaped result for {query}"   # small models parse sentences better than bare values

r = run_agent("the task", tools=[get_thing], skill=DEFAULT_SKILL)   # the loop
r.text, r.cost_usd, r.usage, r.tool_calls                            # everything measured
```

`chat()` for one-shot calls, `cascade()` for cheap-first routing, `run_agent()`
for the tool loop. Provider is one env var (`MODEL_PROVIDER`); see
[docs/SETUP.md](docs/SETUP.md).

## House rules (these earn rubric points)

- **Zero/low-arg tools, sentence-shaped returns.** A 3B local model is the
  default target; keep tools simple.
- **The fixture rule.** Every networked tool checks `AGENT_OFFLINE` and falls
  back to `fixtures/` on *any* exception, with a one-line notice to stderr.
  Evals always run offline so numbers are reproducible.
- **System prompt = role only.** All format/rules live in the SKILL.md, never
  in `agent.py`.
- **Skill anatomy:** `name` == directory name; a trigger-rich `description`
  (what + when); body sections `## Defaults` / `## Workflow` / `## Gotchas` /
  `## Output template`. Validate: `uv run agentskills validate skills/<name>`.
- **Assert outcomes, not rituals.** Eval the brief's *content*, not a magic
  phrase the model happens to print.
- **Budget:** ~300 lines of code per project (the flagship gets ~500). Readable
  beats clever.

## Before you push

```bash
make verify     # the no-model matrix (tests, validate, selftests, lint) — also what CI runs
make smoke      # every project answers offline on your local model
make evals      # full eval pass-rate deltas (needs a local model; slow)
```

CI runs `make verify` on every push and PR. Keep your skill's eval delta ≥ 0,
fill `docs/MODEL_SELECTION.md` with the numbers you measured, and you've cleared
the bar. Then add a row to the picker table in the top-level [README](README.md).

By contributing you agree your work is MIT-licensed, like the rest of the repo.
