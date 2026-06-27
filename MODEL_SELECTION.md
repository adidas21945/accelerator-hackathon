# Model Selection Rationale — Cheap Shot / UnpaidRA

## Signal Choice

We use a single-token logprob softmax over complexity tiers 1, 2, and 3,
grounded in CP-Router (Su et al., 2025), which extracts logits for discrete
answer options and applies softmax to route between model tiers. We explicitly
rejected verbalized confidence — the literature shows it achieves AUC-ROC of
0.56 on GSM8K (Self-Evaluating LLMs for Multi-Step Tasks, arXiv 2511.07364),
barely above random, because small models are systematically overconfident
when asked to self-report. We also considered semantic entropy (Kuhn et al.,
2023) and self-consistency across N samples, but both require multiple forward
passes — incompatible with our enterprise cost efficiency goal. Probe-based
methods outperform verbalization without requiring weight access or training
data (Dynamic Model Routing Survey, arXiv 2603.04445).

## Why Prospective Routing

Prior work including OI-MAS (arXiv 2601.04861, Jan 2026) establishes the
conductor pattern — identifying agent roles and model sizes before execution.
Our system extends this with confidence-based prospective dispatch: the router
runs before any execution agent, using the planner's subtask descriptions as
the complexity signal. This is distinct from reactive cascading (RouteLLM,
Ong et al., 2025) which starts cheap and escalates on failure — our approach
avoids the cost of a failed cheap attempt entirely.

## Tier Justification

- **granite4:micro** — local, zero cost, zero latency. Used for query
  expansion and other templated tasks where output structure is fixed and
  reasoning depth is minimal.
- **claude-haiku-4-5** — mid tier. Strong structured reasoning at low cost.
  Used for per-paper summarization where output quality matters but synthesis
  depth is not required.
- **claude-sonnet-4-6** — frontier. Reserved for gap synthesis and idea
  generation where complex open-ended reasoning directly determines the value
  of the final output.

## Observed Distribution and Cost

From our measured run: granite4:micro ×1, claude-haiku-4-5 ×5,
claude-sonnet-4-6 ×2. Total: 7,728 tokens. Actual cost: $0.014.
All-Sonnet baseline: $0.023. **39.1% cost reduction.**

RouteLLM (Ong et al., 2025) reported 70% cost reduction with a trained router
on Chatbot Arena preference data. We achieve 39.1% with zero training data
and a ~50-token probe per routing decision. The overhead of the entire routing
layer is less than the cost of one summarization call.

## Future Work

Domain-specific threshold tuning, semantic entropy over sampled outputs for
higher-stakes routing decisions, probe fine-tuning on financial research
subtasks.