## Skill plan
- Name: format-engineering-notes
- Purpose: Formats rough engineering notes into a polished how-to page for our internal wiki, Use whenever document or write.

## SKILL.md
```markdown
---
name: format-engineering-notes
description: Formats rough engineering notes into a polished how-to page for our internal wiki, Use whenever document or write.
license: MIT
---

# Format Engineering Notes

Convert unstructured engineering notes into well-organized, professional pages suitable for our internal wiki. This skill ensures clarity, consistency, and completeness in documentation, making it easier for team members to understand and follow technical processes.

## Defaults (do not present options)
- **Title**: `Formatted Engineering Note`
- **Section Headings**: Introduction, Requirements, Steps, Results, Conclusion
- **Tone**: Formal, precise, and instructional
- **Formatting**: Use headings, bullet points, numbered steps, and tables where appropriate

## Workflow
1. **Read the raw notes** to understand the technical content and context.
2. **Identify key sections** such as Introduction, Requirements, Steps, Results, and Conclusion.
3. **Rephrase sentences** for clarity and conciseness while maintaining technical accuracy.
4. **Add missing information**: Include any necessary prerequisites, tools, or resources mentioned in passing.
5. **Format the document**: Apply consistent headings, bullet points, numbered steps, and tables to enhance readability.

## Gotchas
- Ensure that all technical terms are defined for readers unfamiliar with the context.
- Avoid using jargon without explanation unless it's common knowledge within the team.
- Maintain a neutral tone; avoid overly enthusiastic or promotional language.

## Output template
Produce EXACTLY these sections, in this order:

### Title
The title of the wiki page should be concise and descriptive.

### Introduction
A brief overview summarizing the purpose and scope of the engineering note.

### Requirements
List any prerequisites, tools, or resources needed to implement the solution described.

### Steps
Provide a clear, step-by-step guide on how to execute the process. Use numbered lists for clarity.

### Results
Describe the expected outcomes and any metrics that indicate success.

### Conclusion
Summarize the key points and provide any additional context or recommendations.
```

## Validation
Valid skill: /var/folders/w8/hbqbz7yn33q2_2ncx3m9k_sc0000gn/T/skill-forge-xrq4hhv7/format-engineering-notes

## Next steps
- Copy the folder into your project's skills/ and pass it to run_agent(skill=...).
- Add 3 eval cases and run: uv run python -m agentkit.evals <your-project>.
- Re-read the description: it does the routing, so use your tasks' real words.
