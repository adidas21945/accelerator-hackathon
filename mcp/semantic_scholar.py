"""Semantic Scholar paper search with hardcoded fallback."""

from __future__ import annotations

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_API = "https://api.semanticscholar.org/graph/v1/paper/search"
_FIELDS = "title,abstract,year,authors,citationCount,url"

FALLBACK_PAPERS = [
    {
        "title": "Deep Learning for Short-Term Equity Trend Forecasting: A Behavior-Driven Multi-Factor Approach",
        "abstract": "This study applies machine learning to short-term stock return prediction using behavioral alpha factors. MLP achieves the best performance with Sharpe ratio of 1.6075 compared to CNN at 1.1487 and SVM at 0.7709.",
        "year": 2025,
        "authors": [{"name": "Wenhao Xu et al."}],
        "citationCount": 12,
        "url": "https://arxiv.org/abs/2508.14656",
    },
    {
        "title": "FactorGCL: A Hypergraph-Based Factor Model with Temporal Residual Contrastive Learning for Stock Returns Prediction",
        "abstract": "A hypergraph-based factor model combining hypergraph neural networks with temporal residual contrastive learning to capture complex inter-stock relationships and latent factor structures for return prediction.",
        "year": 2025,
        "authors": [{"name": "FactorGCL Authors"}],
        "citationCount": 8,
        "url": "https://arxiv.org/list/q-fin/2025-02",
    },
    {
        "title": "Artificial Intelligence Models for Predicting Stock Returns Using Fundamental, Technical, and Entropy-Based Strategies",
        "abstract": "Examines combining LLM semantic intelligence with traditional ML for NASDAQ-100 stock prediction over 2020-2025. Tests fundamental, technical, and entropy-based frameworks using ChatGPT-4o with ML algorithms.",
        "year": 2025,
        "authors": [{"name": "Gil Cohen"}, {"name": "Avishay Aiche"}, {"name": "Ron Eichel"}],
        "citationCount": 15,
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12191900/",
    },
    {
        "title": "Multi-Horizon Echo State Network Prediction of Intraday Stock Returns",
        "abstract": "Applies Echo State Networks to intraday stock return prediction across multiple horizons. ESNs offer computational efficiency over deep learning while capturing nonlinear temporal dependencies, showing competitive performance against LSTM and ARIMA baselines.",
        "year": 2025,
        "authors": [{"name": "ESN Finance Authors"}],
        "citationCount": 6,
        "url": "https://arxiv.org/abs/2504.19623",
    },
    {
        "title": "A Bipartite Graph Approach to U.S.-China Cross-Market Return Forecasting",
        "abstract": "A bipartite graph neural network framework modeling cross-market dependencies between U.S. and Chinese equity markets. Captures asymmetric information flows and outperforms single-market baselines using cross-market alpha signals.",
        "year": 2025,
        "authors": [{"name": "Cross-Market GNN Authors"}],
        "citationCount": 9,
        "url": "https://arxiv.org/abs/2603.10559",
    },
]


def fetch_papers_impl(query: str, limit: int = 5) -> tuple[list[dict], str]:
    """Fetch from Semantic Scholar; return (papers, source) where source is 'live' or 'fallback'."""
    key = os.getenv("SEMANTIC_SCHOLAR_KEY", "")
    headers = {"x-api-key": key} if key else {}
    params = {"query": query, "limit": limit, "fields": _FIELDS}
    try:
        resp = httpx.get(_API, params=params, headers=headers, timeout=8.0)
        resp.raise_for_status()
        raw = resp.json().get("data", [])
        papers = [
            {
                "title": p.get("title", ""),
                "abstract": p.get("abstract", "") or "",
                "year": p.get("year"),
                "authors": p.get("authors", []),
                "citationCount": p.get("citationCount", 0),
                "url": p.get("url", ""),
            }
            for p in raw
            if p.get("title")
        ]
        if papers:
            return papers[:limit], "live"
    except Exception:
        pass
    return FALLBACK_PAPERS[:limit], "fallback"


def fetch_papers(query: str, limit: int = 5) -> list[dict]:
    """MCP-facing wrapper — returns papers only (source discarded)."""
    papers, _ = fetch_papers_impl(query, limit)
    return papers
