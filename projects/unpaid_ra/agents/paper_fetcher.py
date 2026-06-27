"""paper_fetcher agent — fetches papers via MCP or falls back to fixtures."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from projects.unpaid_ra.events import emit

_FIXTURE = Path(__file__).parent.parent / "fixtures" / "papers.json"
_MCP_SCRIPT = Path(__file__).parent.parent.parent.parent / "mcp" / "semantic_scholar.py"


def _fetch_via_mcp(query: str, limit: int = 5) -> tuple[list[dict], str]:
    """Try to import and call semantic_scholar directly; falls back to fixture."""
    if os.getenv("AGENT_OFFLINE"):
        return _load_fixture(), "fixture"
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("semantic_scholar", str(_MCP_SCRIPT))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        papers = mod.fetch_papers(query, limit)
        source = "mcp" if papers else "fixture"
        return papers or _load_fixture(), source
    except Exception:
        return _load_fixture(), "fixture"


def _load_fixture() -> list[dict]:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def run(subtask: dict, queries: list[str] | None = None) -> list[dict]:
    query = (queries or ["ML models for stock return prediction"])[0]
    t0 = time.perf_counter()
    emit("agent_start", agent="paper_fetcher", model="mcp/fetch_papers", query=query)
    emit("fetch_attempt", query=query)

    papers, source = _fetch_via_mcp(query)
    papers = papers[:5]

    elapsed = round(time.perf_counter() - t0, 2)
    emit("papers_retrieved", count=len(papers), tokens=0, cost=0.00, source=source)
    emit("agent_complete", agent="paper_fetcher", model="mcp/fetch_papers",
         tokens=0, actual_cost=0.00, sonnet_cost=0.00, latency=elapsed)
    return papers
