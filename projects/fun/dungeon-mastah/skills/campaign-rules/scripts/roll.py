"""roll.py — deterministic dice for dungeon-mastah. The players can smell fake dice.

CLI:      python roll.py 2d6+1 [--seed 42]   ->  "2d6+1: [4, 3] +1 = 8"
Library:  from roll import roll_spec          (what the agent's tool imports)
Selftest: python roll.py --selftest           (parser + bounds checks; exit 0/1)

Grammar: NdM or NdM+K / NdM-K, with 1 <= N <= 20 and M one of
4, 6, 8, 10, 12, 20, 100. Anything else is rejected loudly — a wrong roll
narrated confidently is worse than an error the model can correct.
"""

from __future__ import annotations

import argparse
import random
import re
import sys

SIDES = (4, 6, 8, 10, 12, 20, 100)
MAX_DICE = 20
_SPEC = re.compile(r"^\s*(\d{1,3})\s*[dD]\s*(\d{1,3})\s*(?:([+-])\s*(\d{1,3}))?\s*$")


def parse_spec(spec: str) -> tuple[int, int, int]:
    """Parse 'NdM' or 'NdM+/-K' into (n_dice, sides, modifier). ValueError on junk."""
    m = _SPEC.match(spec or "")
    if not m:
        raise ValueError(f"bad dice spec {spec!r} — use NdM or NdM+K, like 1d20+2 or 3d6")
    n, sides = int(m.group(1)), int(m.group(2))
    mod = int(m.group(4)) * (-1 if m.group(3) == "-" else 1) if m.group(3) else 0
    if not 1 <= n <= MAX_DICE:
        raise ValueError(f"{n} dice is out of range — roll 1 to {MAX_DICE} at a time")
    if sides not in SIDES:
        raise ValueError(f"d{sides} is not a real die — pick from d4, d6, d8, d10, d12, d20, d100")
    return n, sides, mod


def roll_spec(spec: str, seed: int | None = None) -> str:
    """Roll a spec and return the table-talk line: '2d6+1: [4, 3] +1 = 8'."""
    n, sides, mod = parse_spec(spec)
    rng = random.Random(seed)  # seed=None -> fresh entropy; seeded -> reproducible
    rolls = [rng.randint(1, sides) for _ in range(n)]
    mod_part = f" {'+' if mod > 0 else '-'}{abs(mod)}" if mod else ""
    return f"{n}d{sides}{mod_part.replace(' ', '')}: {rolls}{mod_part} = {sum(rolls) + mod}"


def _total(line: str) -> int:
    return int(line.rsplit("= ", 1)[1])


def selftest() -> int:
    checks: list[tuple[str, bool]] = []

    def expect(label: str, ok: bool) -> None:
        checks.append((label, ok))
        print(("ok  " if ok else "BAD ") + label)

    # Bounds: 200 rolls of 3d6 all land in 3..18 and actually vary.
    totals = [_total(roll_spec("3d6")) for _ in range(200)]
    expect("200x 3d6 totals all within 3-18", all(3 <= t <= 18 for t in totals))
    expect("3d6 totals vary across rolls", len(set(totals)) > 1)

    # Modifiers shift the range in both directions.
    expect("50x 1d4+3 within 4-7", all(4 <= _total(roll_spec("1d4+3")) <= 7 for _ in range(50)))
    expect("50x 1d4-3 within -2-1", all(-2 <= _total(roll_spec("1d4-3")) <= 1 for _ in range(50)))

    # Seeded rolls are reproducible; the sentence shape is stable.
    expect("seeded rolls are equal", roll_spec("2d6+1", seed=42) == roll_spec("2d6+1", seed=42))
    expect("seeds actually steer the dice",
           any(roll_spec("1d100", seed=i) != roll_spec("1d100", seed=i + 1) for i in range(5)))
    expect("sentence shape 'spec: [rolls] +K = total'",
           re.fullmatch(r"2d6\+1: \[\d, \d\] \+1 = \d+", roll_spec("2d6+1", seed=7)) is not None)

    # The parser accepts the whole legal grammar...
    for good in ("1d4", "3d6", "2d6+1", "1d20-2", " 2D10 + 3 ", "20d100"):
        try:
            parse_spec(good)
            expect(f"accepts {good!r}", True)
        except ValueError:
            expect(f"accepts {good!r}", False)

    # ...and rejects junk loudly (fake dice, bad counts, prose).
    for bad in ("", "d20", "2d", "2d7", "0d6", "21d6", "2d6++1", "1d20+", "3x6", "1d6 fire", "banana"):
        try:
            parse_spec(bad)
            expect(f"rejects {bad!r}", False)
        except ValueError:
            expect(f"rejects {bad!r}", True)

    failed = [label for label, ok in checks if not ok]
    print(f"\nselftest: {len(checks) - len(failed)}/{len(checks)} checks passed")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Roll dice: NdM or NdM+K, real dice only.")
    ap.add_argument("spec", nargs="?", help="e.g. 2d6+1")
    ap.add_argument("--seed", type=int, default=None, help="seed for a reproducible roll")
    ap.add_argument("--selftest", action="store_true", help="exercise parser + bounds; exit 0/1")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.spec:
        ap.error("spec required (or --selftest)")
    try:
        print(roll_spec(args.spec, seed=args.seed))
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
