## Skill plan
- Name: python-premerge-checklist
- Purpose: Use whenever reviewing Python pull requests for merge, running static analysis checks, type annotations verification, and tests; report findings as blocking or non-blocking.

## SKILL.md
```markdown
---
name: python-premerge-checklist
description: Use whenever reviewing Python pull requests for merge, running static analysis checks, type annotations verification, and tests; report findings as blocking or non-blocking.
license: MIT
---

# Python Pre-Merge Checklist

This skill automates the pre-merge review process for Python pull requests, ensuring all code adheres to project standards before merging. It runs static analysis checks, linters, type annotations verification, and tests, then categorizes findings as blocking or non-blocking.

## Defaults (do not present options)
- Linter: `flake8`
- Type checker: `mypy`
- Test runner: `pytest`
- Minimum coverage threshold: `80%`

## Workflow
1. Run `flake8` for code style and syntax errors.
2. Execute `mypy` to verify type annotations are correct.
3. Launch `pytest` to run unit tests.
4. Check test coverage using a coverage report.

## Gotchas
- Ensure all new files have appropriate type hints.
- Avoid adding temporary fixes that bypass checks.
- Verify that the coverage threshold is met before merging.

## Output template
Produce EXACTLY these sections, in this order:
## Findings
List of findings categorized as blocking or non-blocking.
## Recommendations
Suggestions for resolving any blocking issues.
```

## Validation
Valid skill: /var/folders/w8/hbqbz7yn33q2_2ncx3m9k_sc0000gn/T/skill-forge-oqt5ijyg/python-premerge-checklist

## Next steps
- Copy the folder into your project's skills/ and pass it to run_agent(skill=...).
- Add 3 eval cases and run: uv run python -m agentkit.evals <your-project>.
- Re-read the description: it does the routing, so use your tasks' real words.
