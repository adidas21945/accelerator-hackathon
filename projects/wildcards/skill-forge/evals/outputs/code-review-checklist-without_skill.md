```markdown
# Pre-Merge Review Checklist Skill

## Description
This skill automates the running of a pre-merge review checklist on Python pull requests. It evaluates the code changes against a set of criteria to determine if they are ready for merging or require further attention (blocking issues). The skill reports the findings, highlighting any blocking versus non-blocking issues.

## Features
- **Automated Review**: Runs automatically as part of the CI/CD pipeline.
- **Python-Specific Checks**: Focuses on Python code changes, ensuring adherence to best practices and coding standards.
- **Blocking vs. Non-Blocking Issues**: Classifies findings into critical (blocking) and less critical issues that need attention before merging.

## Usage
To use this skill in your project:
1. Integrate the skill into your CI/CD pipeline configuration.
2. Configure the checklist criteria relevant to your project's standards.
3. Run the skill on pull requests to evaluate their readiness for merge.

### Example Configuration

```yaml
# .github/workflows/python-pr-check.yml
name: Python PR Checklist

on:
  pull_request:
    paths:
      - '**/*.py'

jobs:
  review:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'

    - name: Run Pre-Merge Review Checklist
      run: |
        # Install the skill
        pip install pre-merge-review-checklist
        
        # Execute the skill on the pull request files
        pre-merge-review-checklist --input-path .pr-files/*.py
```

## Output
The skill outputs a report detailing:
- **Blocking Issues**: Critical issues that prevent merging.
- **Non-Blocking Issues**: Suggestions for improvement or additional tests.

### Example Report Format

```markdown
# Pre-Merge Review Checklist Report

## Blocking Issues

1. [Issue 1 Description]
2. [Issue 2 Description]

## Non-Blocking Issues

1. [Suggestion 1]
2. [Suggestion 2]
```

## Installation
To install the skill, run:
```bash
pip install pre-merge-review-checklist
```

## Development
If you wish to contribute or modify the skill:
1. Clone this repository.
2. Implement changes in `skill.py`.
3. Test your modifications locally.
4. Submit a pull request for review.

## License
This skill is licensed under the MIT License, allowing free use and modification by anyone.
```

## Validation
FAILED: no fenced SKILL.md block found in the answer - nothing to validate.