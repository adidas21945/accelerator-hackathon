"""UnpaidRA MCP server — exposes fetch_papers tool via FastMCP.

Run: uv run python mcp/server.py
Python adds this script's directory (mcp/) to sys.path[0], so we can
import semantic_scholar directly. We deliberately do NOT add the repo
root to sys.path here to avoid shadowing the installed mcp package.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
import semantic_scholar

app = FastMCP("unpaid-ra")


@app.tool()
def fetch_papers(query: str, limit: int = 5) -> list[dict]:
    """Fetch recent academic papers from Semantic Scholar for a given query."""
    return semantic_scholar.fetch_papers(query, limit)


if __name__ == "__main__":
    app.run()
