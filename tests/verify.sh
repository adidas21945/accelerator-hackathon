#!/usr/bin/env bash
# The no-model verification matrix — exactly what CI runs. For the
# model-dependent checks (each project answering, eval deltas) use
# `bash tests/smoke.sh`. Run from anywhere.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0

run() {  # run() "label" cmd...  — quiet on success, dumps log on failure
  local label="$1"; shift
  printf "  %-34s " "$label"
  if "$@" >/tmp/agentday-verify.log 2>&1; then echo "ok"; else
    echo "FAIL"; sed 's/^/      /' /tmp/agentday-verify.log; fail=1; fi
}

echo "verify: no-model checks (the CI matrix)"
run "unit tests"               uv run pytest tests/ -q
run "eval engine selftest"     uv run python -m agentkit.evals --selftest
run "receipt parser selftest"  uv run python projects/everyday/paypah-trail/skills/expense-report/scripts/parse_receipt.py --selftest
run "dice roller selftest"     uv run python projects/fun/dungeon-mastah/skills/campaign-rules/scripts/roll.py --selftest
run "readme lint"              uv run python tools/lint_readmes.py
run "zeroclaw config parses"   uv run python -c "import tomllib,pathlib;tomllib.loads(pathlib.Path('projects/chief-of-staff/chief-of-stuff/deploy/zeroclaw/config.toml').read_text())"

printf "  %-34s " "all skills validate"
sfail=0
for d in $(find projects -name SKILL.md -exec dirname {} \;); do
  uv run agentskills validate "$d" >/dev/null 2>&1 || { sfail=1; echo; echo "      FAIL $d"; }
done
[ $sfail -eq 0 ] && echo "ok" || fail=1

echo
if [ $fail -eq 0 ]; then echo "verify: ALL GREEN"; else echo "verify: FAILURES above"; fi
exit $fail
