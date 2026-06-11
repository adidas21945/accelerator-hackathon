"""storm-ready — the household storm-readiness agent.

Given a place, it pulls active National Weather Service alerts and the point
forecast, and the storm-prep skill turns them into a calm, prioritized
readiness brief for a real household. When nothing is happening it says so —
an all-clear brief is a first-class result, not a failure. Offline mode
(and any live-API hiccup) serves a recorded severe event from fixtures/,
so the demo always works and always has a storm to show.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
# Self-locate the repo root: plain `python agent.py` works from anywhere,
# no editable install or cwd assumptions.
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "agentkit").is_dir())))

from agentkit import run_agent, tool  # noqa: E402

DEFAULT_SKILL = HERE / "skills" / "storm-prep"
NWS = "https://api.weather.gov"
# api.weather.gov returns 403 for requests with no User-Agent — the marquee
# gotcha of this API. Identify yourself; an email or repo URL is the custom.
HEADERS = {
    "User-Agent": "(AgentDay-Example, storm-ready starter; contact: repo issues)",
    "Accept": "application/geo+json",
}

SYSTEM = (
    "You are Storm Ready, a calm emergency-preparedness assistant for regular "
    "households and community groups. Always check the active alerts and the "
    "forecast with your tools before writing any readiness advice."
)


def _fixture(name: str, notice: str = "") -> dict:
    """Load a recorded NWS response. `notice` prints one line to stderr."""
    if notice:
        print(f"[storm-ready] {notice} — serving fixtures/{name}", file=sys.stderr)
    return json.loads((HERE / "fixtures" / name).read_text(encoding="utf-8"))


def _alerts_text(data: dict, area: str) -> str:
    feats = data.get("features", [])
    if not feats:
        return f"No active NWS alerts for {area} right now."
    lines = [f"{len(feats)} active NWS alert(s) for {area}:"]
    for f in feats[:8]:
        p = f["properties"]
        lines.append(
            f"- {p['event']} (severity: {p['severity']}): {p['headline']}. "
            f"Areas: {p['areaDesc']}. Expires {p['expires']}."
        )
    return "\n".join(lines)


def _forecast_text(data: dict) -> str:
    lines = ["NWS point forecast, next periods:"]
    for p in data["properties"]["periods"][:5]:
        pop = (p.get("probabilityOfPrecipitation") or {}).get("value") or 0
        lines.append(
            f"- {p['name']}: {p['shortForecast']}. Around {p['temperature']}°"
            f"{p['temperatureUnit']}, wind {p['windDirection']} {p['windSpeed']}, "
            f"{pop}% chance of precipitation."
        )
    return "\n".join(lines)


@tool
def get_alerts(area: str):
    """Get active National Weather Service alerts (storms, floods, heat, and
    more) for a US state. Pass the two-letter state code, e.g. "MA" for
    Massachusetts or "RI" for Rhode Island. Always check this first."""
    m = re.search(r"\b[A-Z]{2}\b", str(area).upper())
    if not m:
        return f"'{area}' is not a state code. Call get_alerts again with a two-letter code like MA."
    area = m.group()
    if os.getenv("AGENT_OFFLINE"):
        return _alerts_text(_fixture("alerts-severe-sample.json"), area)
    try:
        r = requests.get(f"{NWS}/alerts/active", params={"area": area}, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return _alerts_text(r.json(), area)
    except Exception as e:
        return _alerts_text(_fixture("alerts-severe-sample.json", f"live NWS alerts failed ({e})"), area)


@tool
def get_forecast(lat: float, lon: float):
    """Get the National Weather Service forecast for a place in the US.
    Pass decimal latitude and longitude: Boston MA is lat 42.36, lon -71.06;
    Worcester MA is lat 42.26, lon -71.8. Returns the next ~5 forecast
    periods with conditions, temperature, and wind."""
    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        return "Pass lat and lon as decimal numbers, e.g. lat 42.36 and lon -71.06 for Boston."
    if os.getenv("AGENT_OFFLINE"):
        return _forecast_text(_fixture("forecast-sample.json"))
    try:
        # The NWS two-step: /points/{lat},{lon} answers with the gridpoint
        # forecast URL to fetch next. Never guess gridpoint URLs yourself.
        pt = requests.get(f"{NWS}/points/{lat:.4f},{lon:.4f}", headers=HEADERS, timeout=10)
        pt.raise_for_status()
        fc = requests.get(pt.json()["properties"]["forecast"], headers=HEADERS, timeout=10)
        fc.raise_for_status()
        return _forecast_text(fc.json())
    except Exception as e:
        return _forecast_text(_fixture("forecast-sample.json", f"live NWS forecast failed ({e})"))


def run(task: str, skill=DEFAULT_SKILL):
    """The agent contract every project honors: run(task, skill=...) -> AgentResult."""
    return run_agent(
        task,
        tools=[get_alerts, get_forecast],
        skill=skill,
        system=SYSTEM,
    )


def main():
    ap = argparse.ArgumentParser(description="Storm Ready — household readiness-brief agent")
    ap.add_argument("task", help='e.g. "Build a storm-readiness brief for Boston, MA."')
    ap.add_argument("--no-skill", action="store_true", help="run without the skill (the eval baseline)")
    ap.add_argument("--offline", action="store_true", help="serve the recorded severe event from fixtures/")
    args = ap.parse_args()
    if args.offline:
        os.environ["AGENT_OFFLINE"] = "1"
    r = run(args.task, skill=None if args.no_skill else DEFAULT_SKILL)
    print(r.text)
    print(
        f"\n[{r.turns} turns · {r.usage['prompt_tokens']}+{r.usage['completion_tokens']} tok"
        f" · ${r.cost_usd} · {r.latency_s}s · tools: {[c[0] for c in r.tool_calls]}]",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
