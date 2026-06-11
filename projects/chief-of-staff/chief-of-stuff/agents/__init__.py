"""chief-of-stuff agents — one hub, three specialists, zero magic.

ingest is deterministic code (parsing is not a judgment call). The three
model-backed specialists each wrap ONE focused chat() call. The orchestrator
composes them with plain Python function calls — that is the entire
delegation mechanism, and it fits on one screen.
"""
