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


async def _run_summarizer(paper: dict, subtask: dict) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, summarizer.run, subtask, paper)


async def run(research_field: str, subtasks: list[dict]) -> dict:
    """Execute all 5 waves and return the complete pipeline output."""
    subtask_map = {s["name"]: s for s in subtasks}

    # Wave 1: query_expander
    emit("wave_start", wave=1, agents=["query_expander"])
    qe_subtask = subtask_map["query_expansion"]
    queries_result = await asyncio.get_event_loop().run_in_executor(
        None, query_expander.run, qe_subtask
    )
    queries = queries_result.get("queries", [research_field])
    emit("wave_complete", wave=1, agents=["query_expander"])

    # Wave 2: paper_fetcher
    emit("wave_start", wave=2, agents=["paper_fetcher"])
    pf_subtask = subtask_map["paper_fetch"]
    papers = await asyncio.get_event_loop().run_in_executor(
        None, paper_fetcher.run, pf_subtask, queries
    )
    emit("wave_complete", wave=2, agents=["paper_fetcher"])

    # Wave 3: summarizer × 5 (parallel)
    emit("wave_start", wave=3, agents=["summarizer"] * len(papers))
    sum_subtask = subtask_map["summarization"]
    summaries = list(await asyncio.gather(
        *[_run_summarizer(paper, sum_subtask) for paper in papers]
    ))
    emit("wave_complete", wave=3, agents=["summarizer"] * len(papers))

    # Wave 4: gap_synthesizer
    emit("wave_start", wave=4, agents=["gap_synthesizer"])
    gs_subtask = subtask_map["gap_synthesis"]
    synthesis = await asyncio.get_event_loop().run_in_executor(
        None, gap_synthesizer.run, gs_subtask, summaries
    )
    emit("wave_complete", wave=4, agents=["gap_synthesizer"])

    # Wave 5: idea_generator
    emit("wave_start", wave=5, agents=["idea_generator"])
    ig_subtask = subtask_map["idea_generation"]
    ideas = await asyncio.get_event_loop().run_in_executor(
        None, idea_generator.run, ig_subtask, synthesis
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
