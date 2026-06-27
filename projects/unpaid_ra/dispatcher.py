"""UnpaidRA dispatcher — orchestrates 5-wave async pipeline."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from projects.unpaid_ra.events import emit
from projects.unpaid_ra.agents import (
    query_expander,
    paper_fetcher,
    summarizer,
    gap_synthesizer,
    idea_generator,
)


async def run(research_field: str, subtasks: list[dict]) -> dict:
    """Execute all 5 waves strictly in order and return the complete pipeline output.

    Each wave fully completes (asyncio.gather awaited) before the next wave_start
    is emitted. asyncio.to_thread wraps the synchronous agents so the event loop
    stays responsive without the deprecated get_event_loop().run_in_executor().
    """
    subtask_map = {s["name"]: s for s in subtasks}

    # Wave 1 — query expansion (sequential)
    emit("wave_start", wave=1, agents=["query_expander"])
    queries_result = await asyncio.to_thread(
        query_expander.run, subtask_map["query_expansion"]
    )
    queries = queries_result.get("queries", [research_field])
    emit("wave_complete", wave=1, agents=["query_expander"])

    # Wave 2 — paper fetch (sequential, needs wave 1)
    emit("wave_start", wave=2, agents=["paper_fetcher"])
    papers = await asyncio.to_thread(
        paper_fetcher.run, subtask_map["paper_fetch"], queries
    )
    emit("wave_complete", wave=2, agents=["paper_fetcher"])

    # Wave 3 — summarization (parallel, needs wave 2)
    # asyncio.gather is fully awaited before any wave 4 code runs.
    emit("wave_start", wave=3, agents=["summarizer"] * len(papers))
    sum_subtask = subtask_map["summarization"]
    summaries = list(await asyncio.gather(
        *[asyncio.to_thread(summarizer.run, sum_subtask, paper) for paper in papers]
    ))
    emit("wave_complete", wave=3, agents=["summarizer"] * len(papers))

    # Wave 4 — gap synthesis (sequential, needs ALL of wave 3)
    emit("wave_start", wave=4, agents=["gap_synthesizer"])
    synthesis = await asyncio.to_thread(
        gap_synthesizer.run, subtask_map["gap_synthesis"], summaries
    )
    emit("wave_complete", wave=4, agents=["gap_synthesizer"])

    # Wave 5 — idea generation (sequential, needs wave 4)
    emit("wave_start", wave=5, agents=["idea_generator"])
    ideas = await asyncio.to_thread(
        idea_generator.run, subtask_map["idea_generation"], synthesis
    )
    emit("wave_complete", wave=5, agents=["idea_generator"])

    return {
        "field": research_field,
        "queries": queries,
        "papers": papers,
        "summaries": summaries,
        "synthesis": synthesis,
        "ideas": ideas,
    }
