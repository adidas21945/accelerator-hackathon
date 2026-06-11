# ADLC Worksheet — storm-ready

## 1. Scope
A household member types a place ("Boston, MA", "Suffolk County"); the agent
returns a five-section readiness brief from live NWS data — or a calm
all-clear when nothing is active. One end-to-end success case: "Build a
storm-readiness brief for Boston, MA" against the severe fixture. Out of
scope: evacuation routing, medical advice, non-US locations, anything beyond
the 48-hour forecast window.

## 2. Design
One agent, two networked tools (`get_alerts`, `get_forecast`) that hide the
NWS API's two traps (mandatory User-Agent; points→gridpoint two-step) and
fall back to recorded fixtures on AGENT_OFFLINE or any live failure — an
emergency tool that dies without wifi is a contradiction. The skill carries
ALL format and judgment (all-clear discipline, calm voice, hazard-tuned
go-bag). Model: local 3B (granite4:micro); see docs/MODEL_SELECTION.md.

## 3. Build
agentkit loop (`run_agent`), ~150 LOC. Fixtures were shaped from live
captures of `alerts/active?area=MA` and the Boston gridpoint forecast, then
re-skinned as a Hurricane Arthur-style late-June event (3 alerts,
Extreme/Severe). Verified live first: no User-Agent → 403, with one → 200.

## 4. Evaluate  ← the loop ran 3 times; this log is the point
3 cases × with/without skill (`evals/evals.json`). Iteration log:
- **v1 (smoke run):** output looked perfect, but the heading read
  "Go‑bag check" — granite had swapped the ASCII hyphen for U+2011
  (non-breaking hyphen). Matched that section on the substring "bag check".
- **v2 bug:** first full eval run scored with-skill **0/3**, all three on
  the SAME assertion: section "Next 48 hours" missing — while the outputs
  plainly showed it. `cat -v` revealed `48M-bM-^@M-/hours`: the model
  inserts U+202F (narrow no-break space) between number and unit, invisibly
  breaking exact-string section matching. Fix: match the stable prefix
  "Next 48" — assert the OUTCOME (section exists, has numbers), don't fight
  a 3B's typography. Result: 3/3 vs 0/3, delta +1.00.
- **v3 (variance check):** full re-run — 3/3 vs 0/3 again; delta +1.00 is
  stable, only latency moves with machine load (36.7 → 54.8 s avg/case).
- Also observed, absorbed by substring matching: granite appends
  parentheticals to headings ("## Do now (what the elderly neighbor should
  do before Saturday)").

## 5. Deploy
README quickstart; zero keys; live NWS by default, `--offline` (or any
network failure, with a one-line stderr notice) serves the committed
fixtures, so it runs end-to-end on a plane or in an outage.

## 6. Observe  ←
The run footer prints turns / tokens / $ / latency / tools on every run.
What the traces taught us: offline smoke = 3 turns, 17.2 s; the live demo
run took 54.8 s — today's real feed had 6 alerts (a Heat Advisory and an Air
Quality Alert among them — the all-hazards gotcha showed up live on day
one), roughly doubling the prompt to ~4.6k tokens. Without-skill runs were
slower than with-skill in both eval runs: structure is speed.

## 7. Iterate
Next loop, in order: (1) the FEMA OpenFEMA disaster-declarations tool;
(2) a `script` assertion enforcing the ≤8-bullet go-bag cap (count_min can't
assert a maximum); (3) severity-based routing — Extreme alerts escalate to a
frontier model via `agentkit.route.cascade`; (4) an SMS-length brief mode.
