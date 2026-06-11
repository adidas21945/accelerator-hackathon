## Skill plan
- Name: City Service Requests Data Brief
- Purpose: A skill that turns a CSV summary of city service requests into a one-page data brief for a non-technical audience.

## SKILL.md
```markdown
---
name: City Service Requests Data Brief
description: A skill that turns a CSV summary of city service requests into a one-page data brief for a non-technical audience.
author: Skill Forge
version: 1.0.0
---

# City Service Requests Data Brief

## Description

This skill takes a CSV (Comma-Separated Values) file containing a summary of city service requests and generates a concise, one-page data brief tailored for a non-technical audience. The generated report highlights key insights, trends, and actionable recommendations based on the provided data.

## Features

1. **CSV Input**: Accepts a CSV file as input, where each row represents a city service request with relevant fields such as date, type of request, location, priority, etc.
2. **Data Analysis**: Analyzes the CSV data to identify patterns, trends, and outliers in the city service requests.
3. **Key Insights**: Summarizes the most important insights from the data, such as the volume of requests over time, top-requested services, areas with the highest number of complaints, etc.
4. **Trend Identification**: Detects any notable trends or changes in the frequency and types of service requests across different periods (e.g., monthly, quarterly).
5. **Actionable Recommendations**: Provides actionable recommendations based on the analyzed data to help city officials prioritize resources and address critical issues effectively.
6. **User-Friendly Formatting**: Presents the generated report in a clear, concise, and visually appealing format suitable for non-technical stakeholders.

## Input Format

The skill expects the input CSV file to have the following structure:
```

## Validation
Validation failed for /var/folders/w8/hbqbz7yn33q2_2ncx3m9k_sc0000gn/T/skill-forge-vev_i5_8/City Service Requests Data Brief:
  - Unexpected fields in frontmatter: author, version. Only ['allowed-tools', 'compatibility', 'description', 'license', 'metadata', 'name'] are allowed.
  - Skill name 'City Service Requests Data Brief' must be lowercase
  - Skill name 'City Service Requests Data Brief' contains invalid characters. Only letters, digits, and hyphens are allowed.

## Next steps
- Copy the folder into your project's skills/ and pass it to run_agent(skill=...).
- Add 3 eval cases and run: uv run python -m agentkit.evals <your-project>.
- Re-read the description: it does the routing, so use your tasks' real words.
