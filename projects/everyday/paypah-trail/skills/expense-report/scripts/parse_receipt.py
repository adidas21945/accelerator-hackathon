"""parse_receipt.py — deterministic receipt parser. No LLM touches receipt bytes.

Usage:  python parse_receipt.py <receipt.txt|receipt.pdf>   -> one JSON object
        python parse_receipt.py --selftest                  -> exit 0/1

Output: {vendor, date (ISO or null), total (float), category_hint,
         lines_count, source_file}

Rules (the part a model always fumbles):
- vendor = first non-empty line, decoration stripped, ALL-CAPS title-cased
- date   = first match of MM/DD/YYYY, MM/DD/YY, YYYY-MM-DD, or "May 14, 2026"
- total  = the largest amount on lines saying TOTAL / AMOUNT DUE — never
  SUBTOTAL or SAVINGS, so a post-tip "AMOUNT DUE" beats a pre-tip "TOTAL"
"""

import json
import re
import sys
from pathlib import Path

MONTHS = {m: i for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}
MONEY = re.compile(r"\$?\s*(\d{1,3}(?:,\d{3})*\.\d{2})\b")
TOTAL_LINE = re.compile(r"(?i)\b(amount\s+due|total)\b")
NOT_A_TOTAL = re.compile(r"(?i)sub\s*-?\s*total|saved|savings")
DATE_PATTERNS = [  # (regex, match -> (year, month, day))
    (re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b"), lambda m: (m[1], m[2], m[3])),
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"), lambda m: (m[3], m[1], m[2])),
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2})\b"), lambda m: ("20" + m[3], m[1], m[2])),
    (re.compile(r"\b([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})\b"),
     lambda m: (m[3], MONTHS.get(m[1][:3].lower(), 0), m[2])),
]
CATEGORY_HINTS = [  # first keyword hit on vendor + body wins
    ("Groceries", r"market|grocer|supermarket|foods"),
    ("Health", r"pharmacy|drug|\brx\b|clinic|vision|dental"),
    ("Home", r"hardware|lumber|paint|home improvement|garden"),
    ("Transport", r"\bgas\b|fuel|mbta|transit|uber|lyft|parking|taxi|toll"),
    ("Dining", r"coffee|cafe|espresso|beans|roast|restaurant|grill|kitchen|"
               r"pizza|diner|tavern|bistro|bakery|\btip\b|server|table \d"),
]


def _clean_vendor(line: str) -> str:
    v = re.sub(r"[^\w&'.\s-]", " ", line)
    v = re.sub(r"\s+", " ", v).strip(" -.")
    return v.title() if v.isupper() else v


def _find_date(text: str) -> str | None:
    for pat, ymd in DATE_PATTERNS:
        m = pat.search(text)
        if m:
            y, mo, d = (int(x) for x in ymd(m))
            if 1 <= mo <= 12 and 1 <= d <= 31:
                return f"{y:04d}-{mo:02d}-{d:02d}"
    return None


def _find_total(lines: list[str]) -> float | None:
    candidates = [
        float(m.group(1).replace(",", ""))
        for ln in lines
        if TOTAL_LINE.search(ln) and not NOT_A_TOTAL.search(ln)
        for m in MONEY.finditer(ln)
    ]
    if candidates:
        return max(candidates)
    every = [float(m.group(1).replace(",", "")) for ln in lines for m in MONEY.finditer(ln)]
    return max(every) if every else None  # fallback: largest amount anywhere


def _category_hint(vendor: str, text: str) -> str:
    for cat, pat in CATEGORY_HINTS:
        if re.search(pat, vendor, re.I) or re.search(pat, text, re.I):
            return cat
    return "Other"


def parse_text(text: str, source: str = "<text>") -> dict:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    vendor = _clean_vendor(lines[0]) if lines else None
    return {
        "vendor": vendor,
        "date": _find_date(text),
        "total": _find_total(lines),
        "category_hint": _category_hint(vendor or "", text),
        "lines_count": len(lines),
        "source_file": source,
    }


def parse_file(path: str | Path) -> dict:
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        text = "\n".join((pg.extract_text() or "") for pg in PdfReader(str(path)).pages)
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
    return parse_text(text, source=path.name)


# ── selftest: mini-receipts with known answers ──────────────────────────────

_CASES = [  # (receipt text, expected vendor, expected ISO date, expected total)
    ("GREEN LEAF MARKET\n05/03/2026 18:42\nMILK 4.29\nYOU SAVED 2.50\nSUBTOTAL 104.29\nTAX 4.66\nTOTAL 108.95\n",
     "Green Leaf Market", "2026-05-03", 108.95),
    ("Beacon Hill Beans\n2026-05-06 07:51\nlatte 6.25\ntotal 6.25\n",
     "Beacon Hill Beans", "2026-05-06", 6.25),
    ("The Salty Cod\nMay 21, 2026\nSubtotal 58.40\nTOTAL 62.49\nTIP 12.00\nAMOUNT DUE 74.49\n",
     "The Salty Cod", "2026-05-21", 74.49),  # post-tip amount due beats pre-tip total
    ("*** BAY STATE HARDWARE ***\n5/14/26\nSKU 110 HINGE 7.49\nTOTAL DUE 53.92\nCASH 60.00\n",
     "Bay State Hardware", "2026-05-14", 53.92),
    ("Corner Mart\nno date printed here\nAmount Due: $1,234.56\n",
     "Corner Mart", None, 1234.56),  # missing date -> null; comma thousands ok
    ("CITY PARKING GARAGE\nDec. 2, 2026\n3 HOURS 12.00\nTOTAL 12.00\n",
     "City Parking Garage", "2026-12-02", 12.0),
]


def selftest() -> int:
    bad = 0
    for text, vendor, date, total in _CASES:
        got = parse_text(text, source="selftest")
        ok = got["vendor"] == vendor and got["date"] == date and got["total"] == total
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'} {vendor!r:<26} -> vendor={got['vendor']!r} "
              f"date={got['date']!r} total={got['total']!r}")
    print(f"selftest: {len(_CASES) - bad}/{len(_CASES)} mini-receipts parse as expected")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"usage: {Path(sys.argv[0]).name} <receipt.txt|receipt.pdf> | --selftest")
    if sys.argv[1] == "--selftest":
        sys.exit(selftest())
    print(json.dumps(parse_file(sys.argv[1])))
