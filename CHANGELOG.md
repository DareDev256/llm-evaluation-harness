# Changelog

## [Unreleased]

### Fixed
- **Judge now loads category-specific prompt rubrics from `prompts/` directory** instead of using hardcoded one-liner prompts. All five category rubrics (factual, summary, synthesis, refusal, rag_grounding) are now properly loaded, with fallback to generic prompt and then a hardcoded default.
- **Config threshold keys corrected** across all YAML configs (`smoke.yaml`, `baseline.yaml`, `candidate.yaml`). Changed `pass_rate_min` to `overall_pass_rate` and `judge_avg_min` to `avg_score` to match what `check_thresholds()` actually recognizes. Previously, thresholds were silently skipped as "UNKNOWN".

### Added
- Tests for judge prompt file loading across all categories, fallback behavior, and missing directory handling.
- Tests for `check_thresholds()` covering overall pass rate, average score, per-category rates, unknown metrics, and empty thresholds.
