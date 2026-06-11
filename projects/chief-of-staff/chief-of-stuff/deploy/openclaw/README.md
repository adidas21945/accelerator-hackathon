# Deploying the skills on OpenClaw

OpenClaw is a hosted-anywhere personal agent gateway that consumes
agentskills.io-format skills — the same SKILL.md files this project ships.
It discovers skills from `<workspace>/skills`, `~/.agents/skills`, or
`~/.openclaw/skills` (configured in `~/.openclaw/openclaw.json`), so the
morning-brief skill drops in unchanged:

```bash
mkdir -p ~/.openclaw/skills
cp -r projects/chief-of-staff/chief-of-stuff/skills/morning-brief ~/.openclaw/skills/
cp -r projects/chief-of-staff/chief-of-stuff/skills/meeting-prep  ~/.openclaw/skills/
```

Point OpenClaw's workspace at your real briefcase directory and any task
that says "morning brief" or "prep:" picks up the templates this project's
evals measured.

## Scheduled morning delivery

OpenClaw's heartbeat/cron facility can run a recurring prompt — schedule
"Build my morning brief for today" for 7:00 weekdays and route the output
to the channel you actually read (the gateway speaks WhatsApp/Telegram/
Slack-style connectors). The skill keeps the output to one screen, which
is exactly what a phone notification wants.

## Security caveat (read this one)

OpenClaw's default posture is permissive — it is a gateway that can reach
messaging surfaces and run tools, and its skill registry accepts
community submissions. Before wiring it to a real briefcase: run it
local-only first; scope every secret down to the single connector that
needs it (no blanket env exports); and treat registry skills as untrusted
input — read any third-party SKILL.md end to end before installing, the
same way you'd review a shell script from the internet (see the event
resource guide, §8, on skill-supply-chain hygiene). Your calendar and
meeting notes are the most personal data you own; deny by default.

Verify on your machine — framework flags/paths move fast.
