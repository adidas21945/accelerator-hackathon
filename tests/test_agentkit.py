"""Foundation tests — no model calls, no network."""

import json
from pathlib import Path

import pytest

from agentkit import estimate_cost, load_skill, tool
from agentkit.evals import check, section


def test_tool_decorator_builds_schema():
    @tool
    def lookup(city: str, limit: int = 5):
        """Find things in a city."""
        return city

    s = lookup._tool_schema["function"]
    assert s["name"] == "lookup"
    assert s["description"] == "Find things in a city."
    assert s["parameters"]["properties"] == {"city": {"type": "string"}, "limit": {"type": "integer"}}
    assert s["parameters"]["required"] == ["city"]


def test_tool_decorator_description_override():
    @tool(description="Custom.")
    def f(x: str):
        return x

    assert f._tool_schema["function"]["description"] == "Custom."


def _write_skill(tmp_path: Path, dirname: str, name: str) -> Path:
    d = tmp_path / dirname
    d.mkdir()
    (d / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill. Use when testing.\n---\n\n# Body\n\nDo the thing.\n"
    )
    return d


def test_load_skill_roundtrip(tmp_path):
    d = _write_skill(tmp_path, "my-skill", "my-skill")
    s = load_skill(d)
    assert s.name == "my-skill" and "Do the thing." in s.body and s.description.startswith("Test")


def test_load_skill_name_mismatch_raises(tmp_path):
    d = _write_skill(tmp_path, "my-skill", "other-name")
    with pytest.raises(ValueError, match="must match"):
        load_skill(d)


def test_estimate_cost():
    usage = {"prompt_tokens": 1_000_000, "completion_tokens": 1_000_000}
    assert estimate_cost("claude-sonnet-4-6", usage) == 18.0
    assert estimate_cost("llama3.1", usage) == 0.0  # local/unknown = $0


OUT = "# Report\n\n## Findings\n- one 5\n- two\n\n## Caveats\n- only caveat\n"


def test_section_extraction():
    assert "- one 5" in section(OUT, "Findings")
    assert "- one 5" not in section(OUT, "Caveats")
    assert section(OUT, "Nope") == ""


def test_section_not_truncated_by_bold_or_subsections():
    out = "## The plan\n**Day 1 — Stew** tasty\n**Day 2 — Soup** quick\n\n### Sub\ndetail\n\n## Next\nx\n"
    sec = section(out, "The plan")
    assert "Day 2" in sec and "detail" in sec and "Next" not in sec


def test_unicode_typography_normalized(tmp_path):
    # granite-style narrow no-break space (U+202F) and non-breaking hyphen (U+2011)
    out = "## Next 48 hours\nRain, 30 mph gusts\n\n## Go‑bag check\n- water\n"
    assert "Rain" in section(out, "Next 48 hours")
    got = check(out, {"type": "regex", "value": "30 mph", "where": "Next 48 hours"},
                project_dir=tmp_path, case={"id": "t"})
    assert got.ok, got.evidence
    assert "water" in section(out, "Go-bag check")


@pytest.mark.parametrize(
    "assertion,expected",
    [
        ({"type": "contains_section", "value": "Caveats"}, True),
        ({"type": "regex", "value": r"two", "where": "Findings"}, True),
        ({"type": "regex", "value": r"two", "where": "Caveats"}, False),
        ({"type": "not_regex", "value": r"TODO"}, True),
        ({"type": "contains", "value": "ONLY CAVEAT"}, True),
        ({"type": "count_min", "pattern": r"^- ", "min": 2, "where": "Findings"}, True),
        ({"type": "count_min", "pattern": r"^- ", "min": 2, "where": "Caveats"}, False),
        ({"type": "numeric_present", "where": "Findings"}, True),
        ({"type": "numeric_present", "where": "Caveats"}, False),
    ],
)
def test_assertions(tmp_path, assertion, expected):
    got = check(OUT, assertion, project_dir=tmp_path, case={"id": "t"})
    assert got.ok is expected, got.evidence


def test_script_assertion(tmp_path):
    (tmp_path / "ck.py").write_text("import sys,json; c=json.loads(sys.argv[1]); sys.exit(0 if 'Report' in sys.stdin.read() and c['id']=='t' else 1)\n")
    got = check(OUT, {"type": "script", "path": "ck.py"}, project_dir=tmp_path, case={"id": "t"})
    assert got.ok, got.evidence


# ── routing (no live model — monkeypatch llm.chat) ─────────────────────────

from agentkit import ChatResult, route  # noqa: E402


def _cr(text):
    return ChatResult(text=text, model="stub", provider="local",
                      usage={"prompt_tokens": 1, "completion_tokens": 1}, latency_s=0.0, cost_usd=0.0)


def test_chatresult_has_tier_default():
    assert _cr("x").tier == "default"


def test_cascade_stays_cheap_when_confident(monkeypatch):
    seq = iter([_cr("the cheap answer"), _cr('{"confidence": 0.95}')])
    monkeypatch.setattr(route.llm, "chat", lambda *a, **k: next(seq))
    r = route.cascade("2+2?", threshold=0.7)
    assert not r.escalated and r.text == "the cheap answer" and r.confidence >= 0.7


def test_cascade_escalates_when_unsure(monkeypatch):
    seq = iter([_cr("weak"), _cr('{"confidence": 0.2}'), _cr("the strong answer")])
    monkeypatch.setattr(route.llm, "chat", lambda *a, **k: next(seq))
    r = route.cascade("hard", threshold=0.7)
    assert r.escalated and r.text == "the strong answer"


def test_cascade_degrades_gracefully_without_strong_key(monkeypatch):
    calls = {"n": 0}

    def fake(*a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            return _cr("local answer")
        if calls["n"] == 2:
            return _cr('{"confidence": 0.1}')
        raise RuntimeError("ANTHROPIC_API_KEY is not set")  # no strong-tier key

    monkeypatch.setattr(route.llm, "chat", fake)
    r = route.cascade("hard", threshold=0.7)
    assert not r.escalated  # never crashes
    assert r.text == "local answer"  # keeps the cheap answer
    assert "unavailable" in r.table_row["note"].lower()
