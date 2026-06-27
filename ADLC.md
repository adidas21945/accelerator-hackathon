# UnpaidRA ADLC (Agent Development Life Cycle)

## 1. Project Overview

### System Name

**UnpaidRA**

### Routing Framework

**Cheap Shot**

### Purpose

UnpaidRA is a multi-agent literature synthesis system that accepts a research field as input and returns:

* Recent papers retrieved via Semantic Scholar MCP
* Structured paper summaries
* Synthesized research gaps
* Novel research directions
* Experiment sketches for proposed ideas

The system is designed for researchers and enterprise teams that require literature synthesis at scale.

Cheap Shot is the modular confidence-based routing layer underlying UnpaidRA. It is designed to operate without training data, requires approximately 50 tokens per routing decision, and prioritizes enterprise cost efficiency.

---

## 2. Prior Work

### CP-Router (Su et al., 2025)

CP-Router introduces logprob-based routing between standard LLMs and Large Reasoning Models, demonstrating that token-level confidence signals can effectively determine when expensive reasoning models should be used.

### Confidence-Driven LLM Router (Zhang & Dimitriadis, USC/Amazon, 2025)

This work proposes semantic entropy as an uncertainty measure for routing decisions, enabling confidence-aware model selection based on uncertainty estimates.

### OI-MAS (arXiv 2601.04861, January 2026)

OI-MAS presents a confidence-aware conductor architecture that dynamically selects models for agents within multi-agent systems.

### RouteLLM (Ong et al., ICLR 2025)

RouteLLM uses preference data to train routing policies and reports approximately 70% cost reduction on MT-Bench while preserving answer quality.

### Self-Evaluating LLMs for Multi-Step Tasks (arXiv 2511.07364)

This work evaluates verbalized confidence estimates and reports an AUC-ROC of 0.56 on GSM8K, indicating limited calibration performance.

### Dynamic Model Routing and Cascading Survey (arXiv 2603.04445)

The survey finds that probe-based routing methods consistently outperform verbalized confidence approaches across dynamic routing settings.

### Semantic Uncertainty (Kuhn et al., ICLR 2023)

Semantic Uncertainty introduces semantic entropy as a principled uncertainty measure for natural language generation tasks.

---

## 3. Scope

### Input

A user provides a research field or topic.

### Outputs

The system returns:

1. Recent papers fetched through Semantic Scholar MCP.
2. Structured summaries of retrieved papers.
3. Identified gaps across the literature.
4. Novel research directions.
5. Experiment sketches for proposed ideas.

### Target Users

* Academic researchers
* Enterprise R&D teams
* Corporate research organizations
* Innovation teams

### Goals

The primary objective is to automate large-scale literature synthesis while minimizing cost through confidence-based model routing.

---

## 4. Requirements

### Functional Requirements

#### FR1: Query Expansion

The system shall expand user research topics into targeted search queries.

#### FR2: Literature Retrieval

The system shall retrieve recent literature using Semantic Scholar MCP.

#### FR3: Paper Summarization

The system shall generate structured summaries for retrieved papers.

#### FR4: Gap Identification

The system shall identify open research gaps across retrieved literature.

#### FR5: Research Ideation

The system shall generate novel research directions and experiment sketches.

#### FR6: Dynamic Routing

The system shall assign models to agents using Cheap Shot routing.

#### FR7: Real-Time Observability

The system shall expose routing decisions, confidence scores, and execution metrics during runtime.

### Non-Functional Requirements

* Zero training data requirements.
* Approximately 50 routing tokens per decision.
* Low-cost operation.
* Parallel execution where possible.
* Transparent routing behavior.
* Modular and extensible architecture.

---

## 5. Design

### Overall Architecture

The system consists of a five-agent pipeline executed across sequential waves.

```text
User Query
     |
     v
Query Expander
     |
     v
Paper Fetcher
     |
     v
+----------------------------------+
| Summarizer x5 (Parallel Agents)  |
+----------------------------------+
     |
     v
Gap Synthesizer
     |
     v
Idea Generator
     |
     v
Final Report
```

### Agent Descriptions

#### Agent 1: Query Expander

Responsibilities:

* Expand research topics.
* Generate search subqueries.
* Improve retrieval coverage.

#### Agent 2: Paper Fetcher

Responsibilities:

* Retrieve papers using Semantic Scholar MCP.
* Collect metadata and abstracts.

This agent uses scripts and MCP tools only and consumes zero model tokens.

#### Agent 3: Summarizers (5 Parallel Agents)

Responsibilities:

* Summarize individual papers.
* Extract methodology, findings, limitations, and contributions.

Five summarization agents execute concurrently.

#### Agent 4: Gap Synthesizer

Responsibilities:

* Aggregate summaries.
* Identify unresolved problems and missing research directions.

#### Agent 5: Idea Generator

Responsibilities:

* Produce novel research ideas.
* Propose experimental designs and evaluation plans.

### Model Tiers

#### Tier 1: granite4:micro

Characteristics:

* Local execution
* Zero cost
* Fast inference

Use Cases:

* Templated tasks
* Query expansion
* Formatting

#### Tier 2: claude-haiku-4-5

Characteristics:

* Moderate cost
* Fast structured reasoning

Use Cases:

* Paper summarization
* Information extraction

#### Tier 3: claude-sonnet-4-6

Characteristics:

* Frontier-level reasoning
* Highest capability

Use Cases:

* Gap synthesis
* Research ideation

### Routing Strategy

Cheap Shot employs **prospective routing**.

Models are assigned before execution rather than through reactive cascading.

Prospective routing was selected because it:

* Avoids duplicate computation.
* Reduces latency.
* Minimizes overall cost.
* Simplifies orchestration.

### Confidence Estimation

Cheap Shot performs routing using a single-token logprob probe.

The router:

1. Presents a subtask description.
2. Requests a confidence token.
3. Extracts token log probabilities.
4. Applies softmax normalization.
5. Produces confidence scores for each model tier.
6. Selects the highest-confidence tier.

### Alternative Approaches Considered

#### Verbalized Confidence

Rejected because:

* AUC-ROC of only 0.56 on GSM8K.
* Poor calibration performance.
* High susceptibility to overconfidence.

#### Semantic Entropy

Rejected because:

* Requires multiple forward passes.
* Introduces significant latency.
* Increases inference cost.

### Wave Structure

```text
Wave 1
-------
Query Expander

Wave 2
-------
Paper Fetcher

Wave 3
-------
Summarizer 1
Summarizer 2
Summarizer 3
Summarizer 4
Summarizer 5
(Parallel Execution)

Wave 4
-------
Gap Synthesizer

Wave 5
-------
Idea Generator
```

---

## 6. Build

### Implemented Components

#### FastMCP Semantic Scholar Server

A FastMCP server was implemented to provide access to Semantic Scholar paper retrieval.

#### Event Emitter

`events.py` emits execution events and writes them to `trace.jsonl`.

#### Router

`router/router.py` uses the Ollama native `/api/chat` endpoint with:

```json
{
  "logprobs": true,
  "top_logprobs": 5
}
```

The router extracts log probabilities and computes routing confidence scores.

#### Planner

The planner generates five subtask definitions corresponding to the agent pipeline.

#### Execution Agents

Five execution agents were implemented.

Each agent:

* Loads an agentskills.io-compliant `SKILL.md` file.
* Executes independently.
* Receives routed model assignments.

#### Async Dispatcher

An asyncio-based dispatcher coordinates wave execution and manages parallel scheduling.

#### User Interface

A Flask UI with Server-Sent Events streams execution information in real time.

Displayed information includes:

* Agent status
* Confidence scores
* Routing decisions
* Cost metrics
* Final outputs

### Tools Used

* Claude Code
* agentkit (`llm.py`, `loop.py`, `route.py`, `evals.py`)
* FastMCP
* Ollama Native API
* Anthropic API

---

## 7. Evaluate

### Evaluation Assertions

| Assertion            | Result     |
| -------------------- | ---------- |
| summaries_structured | PASS (5/5) |
| gaps_cited           | PASS       |
| routing_distributed  | PASS       |

### Evaluation Details

#### summaries_structured

All five summaries satisfied the required structured schema.

#### gaps_cited

All synthesized gaps referenced source paper titles.

#### routing_distributed

Three distinct models participated in execution.

### Routing Distribution

| Model             | Count |
| ----------------- | ----- |
| granite4:micro    | 1     |
| claude-haiku-4-5  | 5     |
| claude-sonnet-4-6 | 2     |

### Cost Evaluation

| Metric              | Value  |
| ------------------- | ------ |
| Total Tokens        | 7,728  |
| Actual Cost         | $0.014 |
| All-Sonnet Baseline | $0.023 |
| Cost Reduction      | 39.1%  |

The evaluation demonstrates that Cheap Shot substantially reduces cost while preserving output quality.

---

## 8. Deploy

### Running the Pipeline

```bash
uv run python projects/unpaid-ra/agent.py "research field"
```

### Running the User Interface

```bash
uv run python projects/unpaid-ra/ui/app.py
```

Open:

```text
http://localhost:5000
```

### Runtime Flags

#### Offline Mode

```bash
--offline
```

Forces fixture-based fallback execution.

#### Replay Mode

```bash
--replay
```

Streams events from `demo_trace.jsonl`.

### UI Features

The UI exposes:

* Wave tabs
* Per-agent confidence bars
* Routing decisions
* Execution metrics
* Research ideas
* Cost savings
* Large-format final outputs

---

## 9. Observe

Execution traces are written to `trace.jsonl`.

### Emitted Events

#### `probe_start`

Indicates that routing confidence estimation has begun.

#### `probe_result`

Contains confidence scores for all model tiers.

#### `routing_decision`

Records:

* Threshold values
* Confidence scores
* Assigned model

#### `agent_start`

Indicates agent execution start.

#### `agent_complete`

Records:

* Token usage
* Actual cost
* Sonnet baseline cost
* Latency

#### `wave_start`

Indicates beginning of a workflow wave.

#### `wave_complete`

Indicates completion of a workflow wave.

#### `run_complete`

Records:

* Generated research ideas
* Total cost
* Total savings
* Final execution metrics

### Observability Features

The UI displays confidence bars showing probabilities assigned to:

* Tier 1
* Tier 2
* Tier 3

Routing decisions are visible before agent outputs arrive, enabling transparent execution monitoring.

---

## 10. Iterate

Future improvements include:

### Semantic Entropy for Open-Ended Tasks

Investigate semantic entropy over sampled outputs for highly open-ended synthesis tasks.

### Workflow-Specific Thresholds

Tune routing thresholds for different workflow categories.

### Probe Fine-Tuning

Fine-tune probes on financial research subtasks and domain-specific examples.

### Expanded Workflow Coverage

Extend Cheap Shot beyond literature review to support:

* Incident response
* Code migration
* Competitive intelligence
* Enterprise knowledge synthesis
