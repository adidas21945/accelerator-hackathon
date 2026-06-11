"""qrious-citizen — the civic-data triage agent for Analyze Boston.

Ask a question about Boston open data ("Which neighborhoods had the most
rodent 311 complaints last year?"). The agent discovers datasets on Analyze
Boston (data.boston.gov, a keyless CKAN API), pulls and tallies records,
and the civic-brief skill forces the answer into a five-section brief:
headline number, sourced data, findings, caveats, reproducible query.
Offline (or when the portal hiccups) every tool serves committed fixtures.
"""

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
# Self-locate the repo root: plain `python agent.py` works from anywhere,
# no editable install or cwd assumptions.
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "agentkit").is_dir())))

from agentkit import run_agent, tool  # noqa: E402

DEFAULT_SKILL = HERE / "skills" / "civic-brief"
CKAN = "https://data.boston.gov/api/3/action"
ROW_LIMIT = 5000  # generous on purpose: CKAN's default of 100 silently truncates counts

SYSTEM = (
    "You are Qrious Citizen, a civic-data analyst for Boston's open data "
    "portal. Always find the dataset with search_datasets and pull rows "
    "with get_records before answering. Report only numbers your tools "
    "returned, and cite the dataset."
)


def _fixture(name: str) -> dict:
    return json.loads((HERE / "fixtures" / name).read_text())["result"]


def _ckan(action: str, params: dict, fixture: str) -> dict:
    """GET one CKAN action. Offline — or on ANY live failure — serve the fixture."""
    if os.getenv("AGENT_OFFLINE"):
        return _fixture(fixture)
    try:
        resp = requests.get(f"{CKAN}/{action}", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()["result"]
    except Exception as e:
        print(f"  [live {action} failed ({type(e).__name__}); serving fixtures/{fixture}]", file=sys.stderr)
        return _fixture(fixture)


def _summarize(resource_id: str, res: dict, where: str) -> str:
    """Deterministic tally of CKAN rows — counting is code's job, not a 3B's."""
    rows = res.get("records", [])
    if where and "_note" in res:  # fixture rows aren't pre-filtered the way CKAN's q does live
        rows = [r for r in rows if where.lower() in json.dumps(r, default=str).lower()]
    if not rows:
        return f"No rows matched {where!r} in resource {resource_id}. Retry with where set to ''."
    total = res.get("total", len(rows))
    kept = [r for r in rows if r.get("case_status") != "Duplicate of Existing Case"]
    dates = sorted(str(r["open_dt"])[:10] for r in rows if r.get("open_dt"))

    def top(field: str, n: int) -> str:
        tally = Counter(str(r[field]) for r in kept if r.get(field))
        return ", ".join(f"{k} {v}" for k, v in tally.most_common(n))

    lines = [
        f"Analyzed {len(rows)} of {total} rows matching {where!r} in resource {resource_id}."
        if where else
        f"Analyzed {len(rows)} of {total} rows in resource {resource_id} "
        "(NO filter: counts below cover ALL case types, not one topic).",
        f"open_dt spans {dates[0]} to {dates[-1]}." if dates else "",
        f"Excluded {len(rows) - len(kept)} 'Duplicate of Existing Case' rows from every count below.",
        f"Counts by neighborhood: {top('neighborhood', 10)}." if any(r.get("neighborhood") for r in kept) else "",
        f"Counts by case_title: {top('case_title', 6)}." if any(r.get("case_title") for r in kept) else "",
        f"Reproduce: {CKAN}/datastore_search?resource_id={resource_id}"
        + (f"&q={where}" if where else "") + f"&limit={ROW_LIMIT}",
        f"Sample row: {json.dumps(rows[0], default=str)[:300]}",
    ]
    return "\n".join(line for line in lines if line)


@tool
def search_datasets(query: str):
    """Search Analyze Boston for datasets about a topic (one or two keywords, e.g. '311' or 'crime'). Always call this first to get the dataset URL and its resource ids."""
    res = _ckan("package_search", {"q": query, "rows": 5}, "package-search-sample.json")
    if not res.get("results"):
        return f"No datasets matched {query!r}. Retry with one broader keyword."
    out = [f"Found {res['count']} datasets for {query!r}:"]
    for d in res["results"]:
        csv_first = sorted(d.get("resources", []), key=lambda r: (r.get("format") or "").upper() != "CSV")
        rs = "; ".join(f"{r.get('name') or 'file'} ({r.get('format')}): resource_id {r['id']}" for r in csv_first[:4])
        notes = " ".join((d.get("notes") or "").split())[:150]
        out.append(f"- {d['title']}: {notes}\n  dataset URL: https://data.boston.gov/dataset/{d['name']}\n  resources: {rs}")
    return "\n".join(out)


@tool
def get_records(resource_id: str, where: str = ""):
    """Pull rows from one dataset resource and tally them. resource_id comes from search_datasets. If the question is about one topic, you MUST set where to that single word (e.g. where='rodent'); use where='' only for questions about all cases. Returns counts by neighborhood and type, the date range, and the exact query to reproduce."""
    params = {"resource_id": resource_id, "limit": ROW_LIMIT, "q": where or None}
    return _summarize(resource_id, _ckan("datastore_search", params, "records-sample.json"), where)


@tool
def run_sql(sql: str):
    """Run a SQL SELECT on the Analyze Boston datastore, e.g. SELECT neighborhood, COUNT(*) FROM "<resource_id>" GROUP BY neighborhood. Last resort: prefer get_records, which already tallies; this endpoint is flaky."""
    if not os.getenv("AGENT_OFFLINE"):
        try:
            resp = requests.get(f"{CKAN}/datastore_search_sql", params={"sql": sql}, timeout=30)
            resp.raise_for_status()
            rows = resp.json()["result"]["records"]
            return f"{len(rows)} rows: {json.dumps(rows[:40], default=str)[:1500]}"
        except Exception as e:
            print(f"  [live datastore_search_sql failed ({type(e).__name__}); serving fixture aggregate]", file=sys.stderr)
    rows = _fixture("records-sample.json")["records"]
    tally = Counter(r["neighborhood"] for r in rows if r.get("case_status") != "Duplicate of Existing Case")
    agg = [{"neighborhood": k, "count": v} for k, v in tally.most_common()]
    return f"(offline: aggregate computed from the fixture sample, duplicates excluded) {json.dumps(agg)}"


def run(task: str, skill=DEFAULT_SKILL):
    """The agent contract every project honors: run(task, skill=...) -> AgentResult."""
    return run_agent(
        task,
        tools=[search_datasets, get_records, run_sql],
        skill=skill,
        system=SYSTEM,
    )


def main():
    ap = argparse.ArgumentParser(description="Qrious Citizen — Boston open-data civic briefs")
    ap.add_argument("task", help='e.g. "Which neighborhoods had the most rodent 311 complaints last year?"')
    ap.add_argument("--no-skill", action="store_true", help="run without the skill (the eval baseline)")
    ap.add_argument("--offline", action="store_true", help="force fixture mode (no network)")
    args = ap.parse_args()
    if args.offline:
        os.environ["AGENT_OFFLINE"] = "1"
    r = run(args.task, skill=None if args.no_skill else DEFAULT_SKILL)
    print(r.text)
    print(
        f"\n[{r.turns} turns · {r.usage['prompt_tokens']}+{r.usage['completion_tokens']} tok"
        f" · ${r.cost_usd} · {r.latency_s}s · tools: {[c[0] for c in r.tool_calls]}]",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
