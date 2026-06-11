---
name: skill-author
description: >-
  Writes a complete, spec-valid SKILL.md from a plain-language job
  description. Use whenever asked to build a skill, write or scaffold a
  SKILL.md, forge a new agent skill, turn a job or workflow into a reusable
  skill, or repair a skill that failed validation.
license: MIT
---

# Skill Author

Turn a job description into ONE complete, installable SKILL.md. A skill is
procedural knowledge for an agent: what an expert does, the one right way
to do it, the traps, and the exact output shape. Write the whole file in a
single pass — never ask questions, never leave blanks.

## Defaults (do not present options)

- Name: 2-4 lowercase words joined by single hyphens (e.g. `support-reply`),
  letters/digits/hyphens only, max 64 chars, never starting or ending with
  a hyphen. Derive it from the job, or use the caller's preferred name.
- Frontmatter: exactly three fields — `name`, `description`, `license: MIT`.
- Description: WHAT the skill does in one clause, then "Use whenever ..."
  naming at least 3 trigger keywords from the job. Under 500 characters.
- Body sections, in this exact order: one intro paragraph, then
  `## Defaults (do not present options)`, `## Workflow`, `## Gotchas`,
  `## Output template`.
- 3-5 bullets or steps per section; the whole file stays under 80 lines.
- Use every default, trap, output section, and trigger keyword the caller
  gave you; invent sensible ones where the caller gave none.

## Workflow

1. Read the job. Decide the skill's single coherent unit of work — a job an
   expert actually performs, not "help with documents".
2. Pick the name (rules above). The file will live in a directory with
   exactly that name, so the name must be valid before anything else.
3. Write the description: WHAT + "Use whenever" + the trigger keywords.
4. Write Defaults that commit to ONE way (numbers, formats, tone), a
   numbered Workflow, Gotchas an expert would warn about, and an Output
   template listing the EXACT section headings every answer must produce.
5. Reply in the four-section format below — nothing before or after it.

## Gotchas

- The description does the routing: a perfect body behind a vague
  description never loads. Pack it with words a real task would contain.
- Only `name`, `description`, `license`, `compatibility`, `allowed-tools`,
  and `metadata` are legal frontmatter fields. Adding `author`, `version`,
  or `tags` fails validation.
- Menus are the #1 skill failure. Defaults must commit ("Servings: 2"),
  never offer choices ("2 or 4, as you prefer").
- Never put ``` fences inside the generated SKILL.md — the forge extracts
  your answer by its outer fence, and nested fences break it. Use single
  backticks for commands.
- Keep the description value free of colons and quote marks so the YAML
  frontmatter stays parseable.

## Output template

Produce EXACTLY these four sections, in this order. Fill every
<angle-bracket> slot with real content — no angle brackets, no unfilled
slots may remain in your answer. The description line must contain the
literal words "Use whenever" followed by the trigger keywords — a
description that only says what the skill does will be rejected. So will a
body missing any of its five parts: intro, `## Defaults (do not present
options)`, `## Workflow`, `## Gotchas`, `## Output template`.

## Skill plan
- Name: <skill-name>
- Purpose: <one line>
- Triggers: <comma-separated keywords>

## SKILL.md
One fenced block containing the COMPLETE file:

```markdown
---
name: <skill-name>
description: <what it does>. Use whenever <trigger keywords>.
license: MIT
---

# <Skill Title>

<One-paragraph intro - the job this skill does, completely.>

## Defaults (do not present options)
- <3-4 committed defaults>

## Workflow
1. <numbered imperative steps>

## Gotchas
- <2-3 traps an expert avoids>

## Output template
Produce EXACTLY these sections, in this order:
## <Section one>
<what goes here, one sentence>
## <Section two>
<what goes here, one sentence>
```

## Validation
<one line - the forge replaces this with the real validator verdict>

## Next steps
- <2-3 bullets - where to install the skill and how to eval it>
