# Changelog

## [1.0.0] - 2026-03-02

### Added
- **Dockerfile** for containerized evaluation runs (non-root user, layered caching)
- **Sample reports** in `reports/` directory demonstrating output format
- **Expanded test suite**: 36 tests covering schemas, rules, judge parsing, thresholds, regression detection, and semantic evaluation
- **Portfolio-grade README** with architecture diagram, evaluation categories table, three-layer scoring explanation, sample output, and trade-offs documentation
- Tests for Pydantic schema validation (TestCase, AdapterConfig, RunConfig, EvalResult)
- Tests for rule edge cases (case insensitivity, empty inputs, no expectations)

### Fixed
- **Judge now loads category-specific prompt rubrics from `prompts/` directory** instead of using hardcoded one-liner prompts. All five category rubrics (factual, summary, synthesis, refusal, rag_grounding) are now properly loaded, with fallback to generic prompt and then a hardcoded default.
- **Config threshold keys corrected** across all YAML configs (`smoke.yaml`, `baseline.yaml`, `candidate.yaml`). Changed `pass_rate_min` to `overall_pass_rate` and `judge_avg_min` to `avg_score` to match what `check_thresholds()` actually recognizes. Previously, thresholds were silently skipped as "UNKNOWN".

## [0.1.0] - 2026-02-20

### Added
- Initial evaluation harness with EvalRunner orchestrator
- Three-layer evaluation: rule-based, semantic similarity, LLM-as-a-Judge
- 5 evaluation categories: factual, summary, synthesis, refusal, rag_grounding
- Pluggable SUT adapters: OpenAI Chat, HTTP RAG, Mock
- CLI tools: `run_eval` (single run) and `compare_runs` (regression detection)
- YAML-based configuration with threshold validation
- Category-specific judge rubrics in `prompts/` directory
- JSONL test case format with Pydantic validation
- GitHub Actions CI pipeline (pytest + smoke eval)
- Report generation: JSON results, CSV metrics, Markdown summary
