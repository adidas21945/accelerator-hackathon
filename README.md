# UnpaidRA

**Give it a research field, get back what took your RA three weeks.**

Powered by **Cheap Shot**, a confidence-based prospective routing framework grounded in **CP-Router (Su et al., 2025)** and the **Confidence-Driven LLM Router (Zhang & Dimitriadis, 2025)**.

---

## What it does

UnpaidRA takes a research field as input and returns:

* Recent papers fetched via Semantic Scholar
* Structured summaries of each paper
* Identified gaps in the literature
* Novel research directions with high-level experiment sketches

The routing layer (**Cheap Shot**) assigns models before any agent runs using a single-token logprob probe:

* **granite4:micro** for simple tasks
* **claude-haiku-4-5** for structured reasoning
* **claude-sonnet-4-6** for complex synthesis

---

## Research grounding

* **CP-Router (Su et al., 2025)** — Introduces logprob-based routing between standard LLMs and Large Reasoning Models.
* **Confidence-Driven LLM Router (Zhang & Dimitriadis, USC/Amazon, 2025)** — Uses semantic entropy as an uncertainty signal for routing decisions.
* **OI-MAS (arXiv 2601.04861, Jan 2026)** — Proposes a confidence-aware conductor architecture for multi-agent model selection.
* **RouteLLM (Ong et al., ICLR 2025)** — Uses preference data to train routers and achieves substantial cost reductions while maintaining quality.
* **Self-Evaluating LLMs for Multi-Step Tasks (arXiv 2511.07364)** — Evaluates verbalized confidence estimates for multi-step reasoning tasks.
* **Dynamic Model Routing and Cascading Survey (arXiv 2603.04445)** — Surveys routing methods and finds probe-based approaches outperform verbalized confidence.
* **Semantic Uncertainty (Kuhn et al., ICLR 2023)** — Introduces semantic entropy as a principled uncertainty measure for natural language generation.

---

## Results

| Metric                                | Value                 |
| ------------------------------------- | --------------------- |
| Cost Reduction vs All-Sonnet Baseline | **39.1%**             |
| Actual Cost per Run                   | **$0.014**            |
| Total Tokens                          | **7,728**             |
| Evaluation Status                     | **3/3 evals passing** |

### Routing Distribution

| Model             | Count |
| ----------------- | ----- |
| granite4:micro    | ×1    |
| claude-haiku-4-5  | ×5    |
| claude-sonnet-4-6 | ×2    |

---

## Setup

```bash
uv sync
ollama pull granite4:micro
cp .env.example .env
```

Add the following variables to `.env`:

```text
ANTHROPIC_API_KEY=your_key_here
SEMANTIC_SCHOLAR_KEY=your_key_here
```

---

## Run pipeline

```bash
uv run python projects/unpaid-ra/agent.py "your research field"
```

---

## Run UI

```bash
uv run python projects/unpaid-ra/ui/app.py
```

Then open:

```text
http://localhost:5000
```

---

## Run evals

```bash
uv run python projects/unpaid-ra/evals/run_evals.py
```

---

## Lane

**Lane 3 — Most Innovative Multi-Agent System**

**TOA Agent Build Day, June 27 2026**

---

## License

MIT
