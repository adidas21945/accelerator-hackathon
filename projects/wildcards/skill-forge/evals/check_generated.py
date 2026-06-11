"""Script assertion for skill-forge: the generated skill must be REAL.

stdin = the agent's four-section answer. We extract the fenced SKILL.md,
write it to a temp directory named from its frontmatter `name`, run the
agentskills validator on that directory, and statically check the authoring
rules the validator does not cover (trigger-rich description, the three
craft sections). Exit 0 = pass; every failure reason goes to stderr.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

FENCE = re.compile(r"```[a-zA-Z]*[ \t]*\n(.*?)\n[ \t]*```", re.S)
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(msg: str):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    out = sys.stdin.read()
    md = next((b.strip() for b in FENCE.findall(out)
               if b.strip().startswith("---") and "name:" in b), None)
    if not md:
        fail("no fenced SKILL.md block with frontmatter in the agent output")
    parts = md.split("---", 2)
    if len(parts) < 3:
        fail("frontmatter is not closed with ---")
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        fail(f"frontmatter is not parseable YAML: {e}")
    name, desc, body = str(meta.get("name", "")), str(meta.get("description", "")), parts[2]

    if not NAME.match(name) or len(name) > 64:
        fail(f"name {name!r} is not lowercase-hyphens (1-64 chars, no edge/double hyphens)")
    if len(desc) < 40:
        fail(f"description is too short to route anything ({len(desc)} chars < 40)")
    if not re.search(r"(?i)\buse\s+(it\s+|this\s+)?when(ever)?\b", desc):
        fail("description has no 'Use when/whenever ...' trigger clause")
    for sec in ("## Defaults", "## Gotchas", "## Output template"):
        if sec.lower() not in body.lower():
            fail(f"generated body is missing the {sec!r} section")

    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / name  # dir name == frontmatter name, by construction
        d.mkdir()
        (d / "SKILL.md").write_text(md + "\n", encoding="utf-8")
        p = subprocess.run(
            [sys.executable, "-m", "skills_ref.cli", "validate", str(d)],
            capture_output=True, text=True, timeout=30,
        )
        if p.returncode != 0:
            fail("validator rejected it: " + " | ".join((p.stdout + p.stderr).strip().splitlines()))

    print(f"ok: {name!r} extracted, craft-checked, and validator-approved", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
