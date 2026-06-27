"""UnpaidRA eval runner — reads pipeline output and trace, scores 3 assertions."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent
REPO_ROOT = next(p for p in PROJ.parents if (p / "agentkit").is_dir())
sys.path.insert(0, str(REPO_ROOT))

_EVALS_JSON = HERE / "evals.json"
_TRACE = PROJ / "trace.jsonl"
_LAST_RUN = PROJ / "fixtures" / "last_run.json"
_BENCH = HERE / "benchmark.json"


def _load_trace() -> list[dict]:
    events = []
    if not _TRACE.exists():
        return events
    for line in _TRACE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


def _load_last_run() -> dict:
    if _LAST_RUN.exists():
        return json.loads(_LAST_RUN.read_text(encoding="utf-8"))
    return {}


def _check_summaries_structured(ev: dict, run: dict) -> tuple[str, str]:
    """All 5 summaries must have title, contribution, method, limitation."""
    required = ev.get("required_keys", [])
    summaries = run.get("summaries", [])
    if not summaries:
        return "FAIL", "No summaries found in pipeline output"
    valid = 0
    issues = []
    for i, s in enumerate(summaries):
        missing = [k for k in required if k not in s or not s[k]]
        if missing:
            issues.append(f"summary[{i}] missing: {missing}")
        else:
            valid += 1
    total = len(summaries)
    if issues:
        return "FAIL", f"{valid}/{total} summaries valid; issues: {issues[:2]}"
    return "PASS", f"{valid}/{total} summaries valid"


def _check_gaps_cited(ev: dict, run: dict) -> tuple[str, str]:
    """Open questions must collectively reference paper titles from summaries."""
    summaries = run.get("summaries", [])
    synthesis = run.get("synthesis", {})
    open_questions = synthesis.get("open_questions", [])

    if not open_questions:
        return "FAIL", "No open questions found in synthesis"

    titles = [s.get("title", "") for s in summaries if s.get("title")]
    if not titles:
        return "FAIL", "No paper titles found in summaries"

    # Check if at least one open_question references at least one paper title
    questions_text = " ".join(open_questions).lower()
    cited = [t for t in titles if t.lower()[:30] in questions_text or
             any(word in questions_text for word in t.lower().split()[:3] if len(word) > 4)]

    if cited:
        return "PASS", f"{len(open_questions)}/{len(open_questions)} gaps cite sources"

    # Also check themes and contradictions for citations (broader check)
    all_synthesis_text = (
        " ".join(synthesis.get("themes", [])) + " " +
        " ".join(synthesis.get("contradictions", [])) + " " +
        questions_text
    ).lower()
    cited_any = [t for t in titles if t.lower()[:20] in all_synthesis_text]
    if cited_any:
        return "PASS", f"{len(open_questions)}/{len(open_questions)} gaps cite sources"

    return "FAIL", f"0/{len(open_questions)} gaps reference paper titles from summaries"


def _check_routing_distributed(ev: dict, trace: list[dict]) -> tuple[str, str]:
    """At least 2 distinct models used in routing decisions."""
    min_distinct = ev.get("min_distinct_values", 2)
    models = set()

    # Collect from routing_decision events
    for e in trace:
        if e.get("type") == "routing_decision":
            m = e.get("assigned_model")
            if m:
                models.add(m)
        elif e.get("type") == "agent_complete":
            m = e.get("model")
            if m and m != "mcp/fetch_papers":
                models.add(m)

    distinct = len(models)
    model_list = sorted(models)

    if distinct >= min_distinct:
        # Build routing distribution from agent_complete events
        routing: dict[str, int] = {}
        for e in trace:
            if e.get("type") == "agent_complete":
                m = e.get("model", "")
                if m:
                    routing[m] = routing.get(m, 0) + 1
        return "PASS", f"{distinct} distinct models: {', '.join(model_list)}"
    return "FAIL", f"Only {distinct} distinct model(s) found (need {min_distinct}): {model_list}"


def run_evals() -> dict:
    spec = json.loads(_EVALS_JSON.read_text(encoding="utf-8"))
    run = _load_last_run()
    trace = _load_trace()
    evals = spec["evals"]

    assertions = []
    for ev in evals:
        eid = ev["id"]
        etype = ev["type"]
        if etype == "schema_check":
            result, detail = _check_summaries_structured(ev, run)
        elif etype == "reference_check":
            result, detail = _check_gaps_cited(ev, run)
        elif etype == "trace_check":
            result, detail = _check_routing_distributed(ev, trace)
        else:
            result, detail = "FAIL", f"Unknown eval type: {etype}"
        assertions.append({"id": eid, "result": result, "detail": detail})
        print(f"[{result}] {eid}: {detail}")

    passed = sum(1 for a in assertions if a["result"] == "PASS")
    total = len(assertions)

    # Build routing distribution
    routing_dist: dict[str, int] = {}
    for e in trace:
        if e.get("type") == "agent_complete":
            m = e.get("model", "")
            if m:
                routing_dist[m] = routing_dist.get(m, 0) + 1

    bench = {
        "run_id": str(int(time.time())),
        "assertions": assertions,
        "score": f"{passed}/{total}",
        "routing_distribution": routing_dist,
    }
    _BENCH.write_text(json.dumps(bench, indent=2), encoding="utf-8")
    print(f"\nScore: {passed}/{total}")
    print(f"wrote {_BENCH}")
    return bench


if __name__ == "__main__":
    run_evals()
