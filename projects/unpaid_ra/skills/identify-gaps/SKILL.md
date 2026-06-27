---
name: identify-gaps
description: >
  Proposes novel research directions and high-level experiment sketches
  based on a literature synthesis. Triggers when an agent needs to
  generate actionable research ideas grounded in identified gaps,
  contradictions, or open questions from a body of literature.
allowed-tools: none
---

## Overview

Transform a research synthesis (themes, contradictions, open questions) into
actionable novel research directions, each with three high-level experiment
sketches and a rationale grounded in a specific identified gap.

## Output Template

See `assets/gaps_template.md` for the expected output structure:

```
## Research Ideas
### Direction: {title}
**Novelty:** {why this is new, citing specific gap}
**Experiments:**
1. {high-level experiment sketch}
2. {high-level experiment sketch}
3. {high-level experiment sketch}
```

## Instructions

1. Read the synthesis carefully: themes, contradictions, and open questions.
2. Propose 2-4 distinct research directions, each targeting a specific gap.
3. **direction**: A clear, specific research direction title.
4. **experiments**: Exactly 3 high-level methodology sketches per direction.
   - Describe WHAT to do and HOW to measure success, not implementation details.
   - Think study designs, not code.
5. **novelty_rationale**: Explain why this direction is new by referencing a specific
   gap, contradiction, or open question from the synthesis.
6. Return valid JSON array.

## Gotchas

- Experiments are high-level methodology sketches only — not implementation details.
  Write "Compare model A to model B on dataset X" not "import torch; model = ...".
- novelty_rationale must reference a specific gap from the synthesis.
- Do not propose directions already covered by the cited papers.
- Each direction must be genuinely novel, not a minor variation of existing work.

## Output Schema

```json
[
  {
    "direction": "Research direction title",
    "experiments": [
      "High-level experiment sketch 1",
      "High-level experiment sketch 2",
      "High-level experiment sketch 3"
    ],
    "novelty_rationale": "Why this is new, citing gap: '...'"
  }
]
```
