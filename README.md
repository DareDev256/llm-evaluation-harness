# LLM Evaluation Harness

[![CI](https://github.com/DareDev256/llm-evaluation-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/DareDev256/llm-evaluation-harness/actions/workflows/ci.yml)

Evaluation and regression testing harness for LLM and RAG systems. Detects quality drift across prompt versions, model swaps, and retrieval configuration changes through a combination of rule-based checks, semantic similarity, and LLM-as-a-Judge scoring.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Layer                              │
│  run_eval.py          compare_runs.py                    │
│  (single run)         (baseline vs candidate)            │
└─────────┬──────────────────────┬────────────────────────┘
          │                      │
          ▼                      ▼
┌──────────────────┐   ┌────────────────────┐
│   EvalRunner     │   │  Regression Detect  │
│  - Load cases    │   │  - Pass→Fail check  │
│  - Route to SUT  │   │  - Semantic drop     │
│  - Score results │   │  - Metrics deltas    │
└──┬───┬───┬───┬───┘   └────────────────────┘
   │   │   │   │
   │   │   │   └─── Latency Tracking (wall time per call)
   │   │   │
   │   │   └─── LLM-as-a-Judge (5 rubrics, 0-10 scoring)
   │   │         ├── factual accuracy
   │   │         ├── summary quality
   │   │         ├── synthesis capability
   │   │         ├── refusal appropriateness
   │   │         └── RAG grounding / citations
   │   │
   │   └─── Semantic Similarity (all-MiniLM-L6-v2 cosine)
   │
   └─── Rule-Based Checks
         ├── must_include / must_not_include
         ├── citation detection ([1], [doc_id])
         └── word count enforcement
                    │
          ┌─────────▼─────────┐
          │  Pluggable SUT    │
          │  (Adapters)       │
          │  ├── OpenAI Chat  │
          │  ├── HTTP RAG API │
          │  └── Mock (CI)    │
          └───────────────────┘
                    │
          ┌─────────▼─────────┐
          │   Report Gen      │
          │  ├── JSON results │
          │  ├── CSV metrics  │
          │  ├── MD summary   │
          │  └── diff.json    │
          └───────────────────┘
```

## Evaluation Categories

The harness tests LLM outputs across 5 quality dimensions, each with a dedicated judge rubric:

| Category | What It Tests | Example |
|----------|--------------|---------|
| **Factual** | Accuracy, hallucination detection, completeness | "What is the capital of France?" |
| **Summary** | Conciseness, key information retention | "Summarize this article in 3 sentences" |
| **Synthesis** | Combining information from multiple sources | "Compare React vs Vue for this use case" |
| **Refusal** | Appropriate rejection of harmful/out-of-scope queries | "How do I hack into a bank?" |
| **RAG Grounding** | Citation accuracy, context usage, source attribution | "What does the document say about X?" |

Each category has a rubric file in `prompts/` with a 0-10 scoring scale:
- **9-10**: Excellent (pass)
- **7-8**: Good with minor issues (pass)
- **4-6**: Partial quality (fail)
- **1-3**: Mostly incorrect (fail)
- **0**: Irrelevant or harmful (fail)

## Three-Layer Evaluation

Every test case is scored on three independent axes:

1. **Rule-Based** — deterministic checks (must-include phrases, forbidden phrases, citation patterns, word limits)
2. **Semantic Similarity** — cosine similarity between output and reference answer using `all-MiniLM-L6-v2`
3. **LLM-as-a-Judge** — GPT-4o scores the output on a rubric-specific 0-10 scale with structured JSON verdicts

A test **passes** when all applicable rules pass AND the judge verdict is "pass" (score >= 7).

## Project Structure

```
llm-evaluation-harness/
├── src/
│   ├── schemas.py                 # Pydantic models (TestCase, EvalResult, etc.)
│   ├── adapters/
│   │   ├── __init__.py            # BaseAdapter ABC
│   │   ├── openai_chat.py         # OpenAI Chat completions adapter
│   │   ├── http_rag.py            # Generic HTTP RAG API adapter
│   │   └── mock_adapter.py        # Deterministic mock for CI
│   ├── cli/
│   │   ├── run_eval.py            # Eval runner CLI + threshold checking
│   │   └── compare_runs.py        # Baseline vs candidate comparison CLI
│   ├── eval/
│   │   ├── runner.py              # EvalRunner orchestrator
│   │   ├── judge.py               # LLM-as-a-Judge with prompt loading
│   │   ├── rules.py               # Rule-based evaluators
│   │   ├── semantic.py            # Semantic similarity (lazy-loaded)
│   │   ├── compare.py             # Regression detection
│   │   └── reporting.py           # Report generation (MD + CSV)
│   └── utils/
│       ├── io.py                  # JSONL/YAML/JSON I/O
│       ├── text.py                # Text utilities
│       └── timing.py              # Latency tracking
├── configs/
│   ├── smoke.yaml                 # Mock mode for CI (no API key needed)
│   ├── baseline.yaml              # Baseline eval config
│   └── candidate.yaml             # Candidate config for A/B testing
├── data/
│   ├── smoke_cases.jsonl          # 2 smoke test cases
│   └── test_cases.jsonl           # Full evaluation dataset
├── prompts/                       # Category-specific judge rubrics
│   ├── judge_prompt_factual.txt
│   ├── judge_prompt_summary.txt
│   ├── judge_prompt_synthesis.txt
│   ├── judge_prompt_refusal.txt
│   ├── judge_prompt_rag_grounding.txt
│   └── judge_prompt_generic.txt   # Fallback rubric
├── tests/                         # pytest suite, 6 files
├── reports/                       # Generated on eval runs
├── .github/workflows/ci.yml       # GitHub Actions pipeline
├── Dockerfile                     # Containerized eval runs
└── requirements.txt
```

## Quick Start

```bash
# Clone and install
git clone https://github.com/DareDev256/llm-evaluation-harness.git
cd llm-evaluation-harness
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Smoke test (mock mode — no API key needed)
python -m src.cli.run_eval --config configs/smoke.yaml

# Full evaluation (requires OPENAI_API_KEY)
cp .env.example .env  # Set your key
python -m src.cli.run_eval --config configs/baseline.yaml

# Compare baseline vs candidate
python -m src.cli.compare_runs \
  --baseline reports/results_baseline.json \
  --candidate reports/results_candidate.json
```

## Docker

```bash
# Build
docker build -t llm-eval-harness .

# Run smoke test
docker run --rm llm-eval-harness \
  python -m src.cli.run_eval --config configs/smoke.yaml

# Run with API key
docker run --rm -e OPENAI_API_KEY=sk-... llm-eval-harness \
  python -m src.cli.run_eval --config configs/baseline.yaml
```

## Configuration

### YAML Config Files

```yaml
# configs/baseline.yaml
adapter:
  type: openai_chat          # openai_chat | http_rag | mock
  model: gpt-4o-mini
  temperature: 0.0
thresholds:
  overall_pass_rate: 0.8     # 80% of tests must pass
  avg_score: 7.0             # Mean judge score >= 7
  factual_pass_rate: 0.9     # 90% of factual tests must pass
enable_semantic: true         # Enable cosine similarity scoring
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | For live evals | OpenAI API key for SUT + judge |
| `RAG_API_URL` | For RAG adapter | Target RAG system URL |
| `RAG_API_KEY` | Optional | Bearer token for RAG API |

### Threshold Metrics

| Metric | Format | Example |
|--------|--------|---------|
| `overall_pass_rate` | Float 0-1 | `0.8` = 80% pass |
| `avg_score` | Float 0-10 | `7.0` = mean judge score |
| `{category}_pass_rate` | Float 0-1 | `factual_pass_rate: 0.9` |

Unknown metrics are reported as `UNKNOWN` (never silently ignored).

## Sample Output

### Smoke Test (Mock Adapter)
```
$ python -m src.cli.run_eval --config configs/smoke.yaml

Evaluating 2 test cases...
  [1/2] smoke_1 (factual) ... PASS (score=10, rules=2/2, 1.2ms)
  [2/2] smoke_2 (summary) ... PASS (score=10, rules=1/1, 0.8ms)

Results: 2/2 passed (100%)
Avg judge score: 10.0
Thresholds: ALL PASSED
```

### Regression Comparison
```
$ python -m src.cli.compare_runs --baseline reports/baseline.json --candidate reports/candidate.json

Comparison Report
─────────────────
Baseline pass rate:  90.0%
Candidate pass rate: 85.0%  (Δ -5.0%)

Baseline judge avg:  8.2
Candidate judge avg: 7.6  (Δ -0.6)

Regressions: 2
  - test_factual_3: Passed in baseline, failed in candidate
  - test_rag_7: Semantic score dropped from 0.91 to 0.72
```

## Trade-offs & Design Decisions

| Decision | Rationale |
|----------|-----------|
| **GPT-4o as judge** | Most capable judge model; cost is acceptable for eval runs (not real-time) |
| **Three-tier prompt fallback** | Category file → generic file → hardcoded default. Graceful degradation |
| **Lazy semantic model loading** | `all-MiniLM-L6-v2` only loaded when `enable_semantic: true`. Avoids 2s+ CI startup penalty |
| **Mock adapter for CI** | Deterministic, zero-cost smoke tests. CI never needs API keys |
| **JSONL test cases** | Line-delimited JSON is streamable and diffable (unlike JSON arrays) |
| **Pydantic schemas** | Strict validation at boundaries; catches config errors before expensive API calls |
| **Rule checks are separate from judge** | Rules are fast, deterministic, and free. Judge adds nuance at API cost |

## Tech Stack

- **Python 3.11+** with Pydantic v2 for validation
- **OpenAI SDK** for SUT calls and LLM-as-a-Judge
- **SentenceTransformers** for semantic similarity
- **pandas** for metric aggregation
- **Rich** for terminal formatting
- **httpx** for async HTTP (RAG adapter)
- **pytest** for testing
- **GitHub Actions** for CI
- **Docker** for containerized runs
