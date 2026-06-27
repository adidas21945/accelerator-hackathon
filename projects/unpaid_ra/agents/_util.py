"""Shared utilities for UnpaidRA agents."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from agentkit import llm
from projects.unpaid_ra.router.router import COST_PER_1K

SKILLS_DIR = Path(__file__).parent.parent / "skills"


def resolve_handle(model_name: str) -> llm.ModelHandle:
    """Map an assigned_model string to a ModelHandle."""
    if model_name in ("granite4:micro",):
        base_url = os.getenv("LOCAL_BASE_URL", "http://localhost:11434/v1")
        api_key = os.getenv("LOCAL_API_KEY", "not-needed")
        client = llm.OpenAI(base_url=base_url, api_key=api_key)
        return llm.ModelHandle(client, model_name, "local", "default")
    if model_name == "claude-haiku-4-5":
        return llm.resolve("anthropic", "cheap")
    if model_name == "claude-sonnet-4-6":
        return llm.resolve("anthropic", "default")
    # Fallback to local
    return llm.resolve("local", "default")


def chat_with_model(
    model_name: str,
    messages: list[dict],
    *,
    json_mode: bool = False,
) -> tuple[str, int]:
    """Call any assigned model. Returns (text, total_tokens)."""
    handle = resolve_handle(model_name)
    kwargs: dict = {
        "model": handle.model,
        "messages": messages,
        "temperature": 0.2,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = handle.client.chat.completions.create(**kwargs)
    text = resp.choices[0].message.content or ""
    u = getattr(resp, "usage", None)
    tokens = (getattr(u, "prompt_tokens", 0) or 0) + (getattr(u, "completion_tokens", 0) or 0)
    return text, tokens
