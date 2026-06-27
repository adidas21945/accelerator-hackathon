"""UnpaidRA Planner — defines 5 subtasks and routes each through the confidence router."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from projects.unpaid_ra.events import emit
from projects.unpaid_ra.router.router import route

_SUBTASK_DEFS = [
    {
        "name": "query_expansion",
        "description": "Generate 3-5 precise academic search queries for the given research field to find recent high-impact papers",
    },
    {
        "name": "paper_fetch",
        "description": "Fetch recent papers from Semantic Scholar using the expanded queries",
    },
    {
        "name": "summarization",
        "description": "Summarize each paper individually into structured contribution, method, and limitation format",
    },
    {
        "name": "gap_synthesis",
        "description": "Identify themes, contradictions, and open questions across all paper summaries",
    },
    {
        "name": "idea_generation",
        "description": "Propose novel research directions and high-level experiment sketches based on identified gaps",
    },
]

_PAPER_FETCH_ROUTE = {
    "assigned_model": "mcp/fetch_papers",
    "tier": "scripts",
    "confidence_scores": None,
    "tokens": 0,
    "cost": 0.00,
}


def plan(research_field: str) -> list[dict]:
    """Return 5 subtask dicts with model assignments for the given research field."""
    emit("agent_start", agent="planner", field=research_field)

    subtasks = []
    for defn in _SUBTASK_DEFS:
        subtask_input = {"field": research_field}
        base = {"name": defn["name"], "description": defn["description"], "input": subtask_input}

        if defn["name"] == "paper_fetch":
            entry = {**base, **_PAPER_FETCH_ROUTE}
        else:
            result = route(base)
            entry = {
                **base,
                "assigned_model": result["assigned_model"],
                "tier": result["tier"],
                "confidence_scores": result["confidence_scores"],
            }

        emit("subtask_defined", name=entry["name"], assigned_model=entry["assigned_model"])
        subtasks.append(entry)

    emit("agent_complete", agent="planner", subtasks=[s["name"] for s in subtasks])
    return subtasks
