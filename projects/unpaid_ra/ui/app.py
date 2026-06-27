"""Flask UI server for UnpaidRA — serves the dashboard and SSE streams."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

_UI_DIR = Path(__file__).parent
_FIXTURES_DIR = _UI_DIR.parent / "fixtures"
_DEMO_TRACE = _FIXTURES_DIR / "demo_trace.jsonl"
_LIVE_TRACE = _UI_DIR.parent / "trace.jsonl"
_AGENT_SCRIPT = _UI_DIR.parent / "agent.py"
_ROOT = _UI_DIR.parent.parent.parent

app = Flask(__name__, static_folder=str(_UI_DIR))


@app.route("/")
def index():
    return send_from_directory(str(_UI_DIR), "index.html")


def _sse_line(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


@app.post("/run")
def run_agent():
    """Start the agent pipeline for a given research field."""
    data = request.get_json(force=True) or {}
    field = data.get("field", "ML models for stock return prediction").strip() or \
            "ML models for stock return prediction"
    # Clear trace so /stream starts fresh
    _LIVE_TRACE.write_text("", encoding="utf-8")
    subprocess.Popen(
        ["uv", "run", "python", str(_AGENT_SCRIPT), field],
        cwd=str(_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return jsonify({"status": "started"})


@app.route("/stream")
def stream():
    """Tail trace.jsonl as SSE. The agent must already be running (started via /run)."""

    def generate():
        yield _sse_line({"type": "stream_open", "mode": "live"})
        seen = 0
        deadline = time.perf_counter() + 120  # 2-min hard cap
        while time.perf_counter() < deadline:
            time.sleep(0.15)
            try:
                lines = _LIVE_TRACE.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for line in lines[seen:]:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                    yield _sse_line(ev)
                    seen += 1
                    if ev.get("type") == "run_complete":
                        return
                except json.JSONDecodeError:
                    pass

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/replay")
def replay():
    """Stream demo_trace.jsonl as SSE, compressing 45s of real time into ~4s."""

    def generate():
        yield _sse_line({"type": "stream_open", "mode": "replay"})
        lines = _DEMO_TRACE.read_text(encoding="utf-8").splitlines()
        events = [json.loads(l) for l in lines if l.strip()]
        if not events:
            return
        t_start = events[0]["ts"]
        t_end = events[-1]["ts"]
        total_real = max(t_end - t_start, 1.0)
        target_duration = 4.0

        wall_start = time.perf_counter()
        for ev in events:
            frac = (ev["ts"] - t_start) / total_real
            target_wall = wall_start + frac * target_duration
            now = time.perf_counter()
            if target_wall > now:
                time.sleep(target_wall - now)
            yield _sse_line(ev)

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"UnpaidRA UI → http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
