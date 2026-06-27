"""Shared utilities for UnpaidRA agents."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from agentkit import llm
from projects.unpaid_ra.router.router import COST_PER_1K

SKILLS_DIR = Path(__file__).parent.parent / "skills"

_LOCAL_BASE_URL = "http://localhost:11434/v1"
_LOCAL_MODEL = "granite4:micro"


def _local_handle() -> llm.ModelHandle:
    base_url = os.getenv("LOCAL_BASE_URL", _LOCAL_BASE_URL)
    api_key = os.getenv("LOCAL_API_KEY", "not-needed")
    model = os.getenv("LOCAL_MODEL", _LOCAL_MODEL)
    client = llm.OpenAI(base_url=base_url, api_key=api_key)
    return llm.ModelHandle(client, model, "local", "default")


def resolve_handle(model_name: str) -> llm.ModelHandle:
    """Map an assigned_model string to a ModelHandle.

    When AGENT_OFFLINE=1 all calls are routed to the local Ollama server so
    every agent call produces real token counts without needing API keys.
    The assigned_model name is preserved in agent_complete events by the
    individual agent callers — only the underlying endpoint changes here.
    """
    if os.getenv("AGENT_OFFLINE"):
        return _local_handle()
    if model_name == "granite4:micro":
        return _local_handle()
    if model_name == "claude-haiku-4-5":
        return llm.resolve("anthropic", "cheap")
    if model_name == "claude-sonnet-4-6":
        return llm.resolve("anthropic", "default")
    # Fallback: try local rather than crashing
    return _local_handle()


def chat_with_model(
    model_name: str,
    messages: list[dict],
    *,
    json_mode: bool = False,
) -> tuple[str, int]:
    """Call any assigned model. Returns (text, total_tokens).

    total_tokens = prompt_tokens + completion_tokens from the API response.
    """
    handle = resolve_handle(model_name)
    kwargs: dict = {
        "model": handle.model,
        "messages": messages,
        "temperature": 0.2,
    }
    # Anthropic's compat endpoint rejects json_object; only set for local Ollama.
    # All agent prompts already instruct "Return ONLY valid JSON" so this is safe.
    if json_mode and handle.provider == "local":
        kwargs["response_format"] = {"type": "json_object"}
    resp = handle.client.chat.completions.create(**kwargs)
    text = resp.choices[0].message.content or ""
    u = getattr(resp, "usage", None)
    prompt_tok = getattr(u, "prompt_tokens", 0) or 0
    completion_tok = getattr(u, "completion_tokens", 0) or 0
    return text, prompt_tok + completion_tok
