## Skill plan
- Name: Engineering Notes Formatter
- Purpose: The Engineering Notes Formatter skill is designed to take rough engineering notes as input and format them into a polished, well-structured how-to page for our internal wiki. This skill aims to streamline the process of documenting technical information by automatically organizing content, applying consistent formatting, and generating relevant metadata.

## SKILL.md
```markdown
---
name: Engineering Notes Formatter
description: The Engineering Notes Formatter skill is designed to take rough engineering notes as input and format them into a polished, well-structured how-to page for our internal wiki. This skill aims to streamline the process of documenting technical information by automatically organizing content, applying consistent formatting, and generating relevant metadata.
tags:
  - Skill
  - Engineering
  - Documentation
---

# Engineering Notes Formatter

## Description

The Engineering Notes Formatter skill is designed to take rough engineering notes as input and format them into a polished, well-structured how-to page for our internal wiki. This skill aims to streamline the process of documenting technical information by automatically organizing content, applying consistent formatting, and generating relevant metadata.

## Features

### 1. Input Parsing
- Accepts rough engineering notes in plain text or markdown format.
- Identifies key sections such as introduction, materials, steps, results, and conclusions.

### 2. Structured Formatting
- Converts the input into a well-structured wiki page with appropriate headings and subheadings.
- Applies consistent formatting for code snippets, equations, and diagrams.
- Ensures proper indentation and line breaks for readability.

### 3. Content Organization
- Groups related information under relevant sections based on predefined categories or tags.
- Creates separate pages for each major topic if the input is extensive.
- Maintains a logical flow of content within each page.

### 4. Metadata Generation
- Extracts key metadata from the input, such as project name, author, date, and version.
- Generates a summary section that highlights the main points and outcomes of the notes.
- Creates an index or table of contents for easy navigation.

### 5. Style Enhancement
- Applies consistent styling to headings, lists, and code blocks throughout the page.
- Ensures proper grammar, spelling, and punctuation in the formatted text.
- Incorporates relevant wiki-specific formatting tags (e.g., [[link|description]], {{template}}).

## Usage

To use the Engineering Notes Formatter skill, follow these steps:

1. Prepare your rough engineering notes by writing them in plain text or markdown format.
2. Ensure that you have included all necessary information such as materials, steps, results, and conclusions.
3. Run the Engineering Notes Formatter skill with your input notes as the argument.
4. The skill will process the input and generate a polished how-to page ready for publication on the internal wiki.

## Example

**Input:**
```

## Validation
Validation failed for /var/folders/w8/hbqbz7yn33q2_2ncx3m9k_sc0000gn/T/skill-forge-x_uw07sp/Engineering Notes Formatter:
  - Unexpected fields in frontmatter: tags. Only ['allowed-tools', 'compatibility', 'description', 'license', 'metadata', 'name'] are allowed.
  - Skill name 'Engineering Notes Formatter' must be lowercase
  - Skill name 'Engineering Notes Formatter' contains invalid characters. Only letters, digits, and hyphens are allowed.

## Next steps
- Copy the folder into your project's skills/ and pass it to run_agent(skill=...).
- Add 3 eval cases and run: uv run python -m agentkit.evals <your-project>.
- Re-read the description: it does the routing, so use your tasks' real words.
