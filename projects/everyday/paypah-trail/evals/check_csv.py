"""check_csv.py — script assertion: the ## Ledger CSV is real, parseable data.

Reads the agent's full output on stdin (case JSON arrives as argv[1] and is
unused). Pass = a ```csv fenced block exists, csv-parses, has the exact
header date,vendor,category,total, >= 4 data rows, every total is a float,
and every category is one of the allowed six. Exit 0/1, reason on stderr.
"""

import csv
import io
import re
import sys

ALLOWED = {"Groceries", "Dining", "Transport", "Health", "Home", "Other"}


def fail(msg: str):
    print(f"check_csv: FAIL — {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    out = sys.stdin.read()
    m = re.search(r"```csv\s*\n(.*?)```", out, re.S | re.I)
    if not m:
        fail("no ```csv fenced block found")
    rows = [r for r in csv.reader(io.StringIO(m.group(1).strip())) if r]
    if not rows:
        fail("csv block is empty")
    header = [c.strip().lower() for c in rows[0]]
    if header != ["date", "vendor", "category", "total"]:
        fail(f"header is {rows[0]!r}, expected date,vendor,category,total")
    data = rows[1:]
    if len(data) < 4:
        fail(f"only {len(data)} data rows, need >= 4")
    for i, r in enumerate(data, 2):
        if len(r) != 4:
            fail(f"row {i} has {len(r)} fields: {r!r}")
        try:
            float(r[3].strip().lstrip("$"))
        except ValueError:
            fail(f"row {i} total {r[3]!r} does not parse as a number")
        if r[2].strip().title() not in ALLOWED:
            fail(f"row {i} category {r[2]!r} not in {sorted(ALLOWED)}")
    print(f"check_csv: ok ({len(data)} ledger rows)", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
