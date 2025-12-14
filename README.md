# LLM Evaluation Harness

Evaluation and regression testing harness for LLM/RAG systems. Detects quality drift across prompt versions, models, and retrieval configurations.

## Features
- **Dataset-driven evaluation**: Define test cases in JSONL.
- **Pluggable SUT**: Supports OpenAI Chat and generic HTTP RAG APIs.
- **Multi-modal evaluation**:
  - Rule-based (inclusion/exclusion/regex)
  - Semantic similarity (sentence-transformers)
  - LLM-as-a-Judge (rubric based)
- **Regression testing**: Compare baseline vs candidate runs.
- **CI/CD ready**: CLI tools and GitHub Actions integration.

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
Copy `.env.example` to `.env` and set your keys.
```bash
cp .env.example .env
```

### Running Evals
```bash
# Smoke test (Mock mode)
python -m src.cli.run_eval --config configs/smoke.yaml

# Full run
python -m src.cli.run_eval --config configs/baseline.yaml
```

### Comparing Runs
```bash
python -m src.cli.compare_runs --baseline reports/results_baseline.json --candidate reports/results_candidate.json
```
