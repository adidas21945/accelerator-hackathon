#!/usr/bin/env bash
# Smoke every starter end-to-end: local model, offline fixtures, zero keys.
# Usage (from the repo root):  bash tests/smoke.sh
set -u
cd "$(dirname "$0")/.."
export MODEL_PROVIDER=local AGENT_OFFLINE=1

declare -a NAMES TASKS
NAMES=(
  "projects/everyday/fridge-whisperer"
  "projects/everyday/paypah-trail"
  "projects/social-good/qrious-citizen"
  "projects/social-good/storm-ready"
  "projects/chief-of-staff/chief-of-stuff"
  "projects/fun/dungeon-mastah"
  "projects/fun/wicked-smaht-bahtendah"
  "projects/wildcards/model-matchmakah"
  "projects/wildcards/skill-forge"
)
TASKS=(
  "I have chicken thighs, broccoli, and rice. Plan 3 dinners for 2 people."
  "Summarize my receipts for May 2026."
  "Which neighborhoods had the most rodent 311 cases in the last year?"
  "Build a storm-readiness brief for Boston, MA."
  "Build my morning brief for Friday, June 26, 2026."
  "Start a one-shot adventure in a haunted Boston brownstone."
  "Something refreshing with mint and lime for a hot day."
  "What is the capital of Massachusetts?"
  "a skill that formats stand-up updates for a small engineering team"
)

fails=0
for i in "${!NAMES[@]}"; do
  name="${NAMES[$i]}"
  if out=$(uv run python "$name/agent.py" "${TASKS[$i]}" 2>/dev/null) && [ -n "$out" ]; then
    echo "PASS  $name"
  else
    echo "FAIL  $name"
    fails=$((fails + 1))
  fi
done

echo
echo "smoke: $(( ${#NAMES[@]} - fails ))/${#NAMES[@]} projects answered offline on the local model"
exit "$fails"
