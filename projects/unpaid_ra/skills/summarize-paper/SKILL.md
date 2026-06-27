---
name: summarize-paper
description: >
  Summarizes a single academic paper into a structured
  contribution/method/limitation format. Triggers when an agent
  needs to extract and structure key information from a paper abstract
  for use in downstream research synthesis tasks.
allowed-tools: none
---

## Overview

Extract the key information from an academic paper abstract into a structured format
with exactly four fields: title, contribution, method, and limitation.

## Output Template

See `assets/summary_template.md` for the expected output structure:

```
## Paper Summary
**Title:** {title}
**Contribution:** {one sentence}
**Method:** {approach used}
**Limitation:** {key weakness or gap}
```

## Instructions

1. Read the provided title and abstract carefully.
2. Fill in each field using only information explicitly stated in the abstract.
3. **contribution**: One sentence maximum. State the main novel claim or result.
4. **method**: Describe the core technique, architecture, or approach used.
5. **limitation**: Identify one key weakness, gap, or constraint mentioned or implied.
6. Return valid JSON matching the output schema.

## Gotchas

- Do not hallucinate citations, results, or claims not present in the abstract.
- Contribution must be one sentence — do not exceed this.
- Stay grounded: only report what the abstract actually states.
- If a field is genuinely absent from the abstract, write "Not stated in abstract".
- Do not paraphrase so aggressively that meaning is lost — keep technical terms.

## Output Schema

```json
{
  "title": "string",
  "contribution": "one sentence",
  "method": "approach description",
  "limitation": "key weakness or gap"
}
```
