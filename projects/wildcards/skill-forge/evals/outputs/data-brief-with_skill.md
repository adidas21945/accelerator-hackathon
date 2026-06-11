## Skill plan
- Name: csv-to-data-brief
- Purpose: Turns a CSV summary of city service requests into a one-page data brief for a non-technical audience. Use whenever you need to present concise insights from request data.

## SKILL.md
```markdown
---
name: csv-to-data-brief
description: Turns a CSV summary of city service requests into a one-page data brief for a non-technical audience. Use whenever you need to present concise insights from request data.
license: MIT
---

# City Service Requests Data Brief

This skill generates a clear, one-page data brief from a CSV file containing city service request summaries. It highlights key trends, top services requested, and any notable patterns that are easy for non-technical stakeholders to understand.

## Defaults (do not present options)
- **Output format**: PDF
- **Page size**: Letter
- **Tone**: Plain language

## Workflow
1. **Read CSV file** containing columns: `service_type`, `count`, `date`.
2. **Calculate totals** for each service type.
3. **Identify top 5 services** by request count.
4. **Summarize trends** over the last month (e.g., increasing, decreasing).
5. **Generate PDF brief**: includes title, key insights, and a simple chart visualizing top services.

## Gotchas
- Ensure CSV has headers: `service_type`, `count`, `date`.
- Missing or malformed data in `service_type` may cause errors.
- The skill assumes the CSV represents a rolling 30-day period without explicit date ranges.

## Output template
Produce EXACTLY these sections, in this order:

## Executive Summary
A brief overview of total requests and top services.

## Key Insights
- Top 5 service types by request count.
- Any significant increase or decrease compared to previous periods.

## Recommendations
- Suggested actions based on service trends (e.g., prioritize training for high-demand services).

## Visualizations
- Simple bar chart showing the distribution of service requests across top categories.
```

## Validation
Valid skill: /var/folders/w8/hbqbz7yn33q2_2ncx3m9k_sc0000gn/T/skill-forge-gjvll15_/csv-to-data-brief

## Next steps
- Copy the folder into your project's skills/ and pass it to run_agent(skill=...).
- Add 3 eval cases and run: uv run python -m agentkit.evals <your-project>.
- Re-read the description: it does the routing, so use your tasks' real words.
