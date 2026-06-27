---
name: synthesize-research
description: >
  Identifies themes, contradictions, and open questions across
  multiple paper summaries. Triggers when an agent needs to
  synthesize patterns and tensions across a body of literature
  to surface what is known, disputed, and unexplored.
allowed-tools: none
---

## Overview

Analyze a set of structured paper summaries and produce a synthesis identifying
common themes, contradictions between papers, and open questions not addressed
by any paper.

## Output Template

See `assets/synthesis_template.md` for the expected output structure:

```
## Research Synthesis
**Themes:**
- {theme} [cite: paper title]

**Contradictions:**
- {paper A} vs {paper B}: {what they disagree on}

**Open Questions:**
- {question not addressed by any paper}
```

## Instructions

1. Read all paper summaries carefully before writing anything.
2. **themes**: Identify 2-4 recurring patterns or claims. Each theme must cite at least one paper by exact title.
3. **contradictions**: Find pairs of papers that make conflicting claims. Name both papers explicitly.
4. **open_questions**: Identify gaps — problems none of the papers address or solve.
5. Return valid JSON matching the output schema.

## Gotchas

- Every theme must cite at least one paper title using `[cite: Paper Title]` notation.
- Contradictions must name both papers that disagree — do not write vague "some papers disagree".
- Do not introduce information not present in the summaries.
- Open questions should be specific and actionable, not generic ("more research needed").
- Themes, contradictions, and open_questions must each be non-empty arrays.

## Output Schema

```json
{
  "themes": ["theme description [cite: Paper Title]"],
  "contradictions": ["Paper A vs Paper B: specific disagreement"],
  "open_questions": ["specific unanswered research question"]
}
```
