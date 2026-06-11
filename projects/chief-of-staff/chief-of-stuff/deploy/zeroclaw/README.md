# Deploying chief-of-stuff on ZeroClaw

ZeroClaw is a single-binary agent runtime written in Rust: one executable,
deny-by-default allowlists for tools, files, and network, and an
OpenAI-compatible provider layer. You approve what the agent may touch;
everything else is refused.

That posture is exactly the shape of this project:

- The **briefcase is local files** (calendar.ics, todos.md, meeting-notes/,
  feeds/) — allowlist that one directory read-only and the agent physically
  cannot wander into the rest of your disk.
- The **default model is local** (granite4:micro via Ollama), so a morning
  brief runs with zero network egress. The frontier prioritizer upgrade is
  one explicit allowlist entry, not a default.

## Setup

1. Install ZeroClaw via the official installer script, then `zeroclaw
   quickstart`.
2. Copy `config.toml` from this directory into `~/.zeroclaw/config.toml`
   (it defines the `local` provider; the Anthropic block is commented).
3. Allowlist the briefcase directory and the agent entrypoint:
   `uv run python projects/chief-of-staff/chief-of-stuff/agent.py`.

## The 7am cron

The whole point of a morning brief is that nobody asks for it. Schedule it:

```cron
0 7 * * 1-5  cd ~/AgentDay-Example && MODEL_PROVIDER=local uv run python \
  projects/chief-of-staff/chief-of-stuff/agent.py \
  "Build my morning brief for today." > ~/brief-today.md 2>> ~/brief.log
```

ZeroClaw's own scheduler can wrap the same command once the binary is
allowlisted. Verify flags and config paths on your machine — framework
defaults move fast.
