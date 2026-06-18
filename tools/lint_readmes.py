"""Lint every project README for the house structure. No deps, no model.

Run:  uv run python tools/lint_readmes.py   (exit 0 = all good)
Each project README must carry the metadata line and the five sections every
starter shares, so the picker promise ("they all look the same") stays true.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEED = ["> Theme:", "## Pitch", "## Quickstart", "## Demo script",
        "## Make it yours", "## Rubric mapping"]


def main() -> int:
    readmes = sorted(ROOT.glob("projects/*/*/README.md"))
    if not readmes:
        print("no project READMEs found", file=sys.stderr)
        return 1
    fails = 0
    for r in readmes:
        text = r.read_text(encoding="utf-8")
        missing = [s for s in NEED if s not in text]
        rel = r.relative_to(ROOT).parent.name
        if missing:
            fails += 1
            print(f"FAIL  {rel:24s} missing: {', '.join(missing)}")
        else:
            print(f"ok    {rel}")
    print(f"\nreadme lint: {len(readmes) - fails}/{len(readmes)} project READMEs well-formed")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
