"""Semantic Scholar paper search with fixture fallback."""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

_FIXTURE = Path(__file__).parent.parent / "projects" / "unpaid-ra" / "fixtures" / "papers.json"
_API = "https://api.semanticscholar.org/graph/v1/paper/search"
_FIELDS = "title,abstract,year,authors,citationCount,url"


def _load_fixture() -> list[dict]:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def fetch_papers(query: str, limit: int = 5) -> list[dict]:
    """Search Semantic Scholar; silently falls back to fixture on any failure."""
    key = os.getenv("SEMANTIC_SCHOLAR_KEY", "")
    headers = {"x-api-key": key} if key else {}
    params = {"query": query, "limit": limit, "fields": _FIELDS}
    try:
        resp = httpx.get(_API, params=params, headers=headers, timeout=15.0)
        resp.raise_for_status()
        raw = resp.json().get("data", [])
        papers = []
        for p in raw:
            papers.append({
                "title": p.get("title", ""),
                "abstract": p.get("abstract", ""),
                "year": p.get("year"),
                "authors": p.get("authors", []),
                "citationCount": p.get("citationCount", 0),
                "url": p.get("url", ""),
            })
        return papers[:limit] if papers else _load_fixture()
    except Exception:
        return _load_fixture()
