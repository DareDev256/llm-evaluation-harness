import pytest
from src.cli.run_eval import check_thresholds
from src.schemas import EvalResult, JudgeResult


def _make_result(test_id="1", category="factual", passed=True, score=8.0):
    return EvalResult(
        test_id=test_id,
        category=category,
        output_text="test",
        rule_results=[],
        semantic_score=0.0,
        judge_result=JudgeResult(
            score=score, verdict="pass" if passed else "fail",
            reasons=[], confidence=1.0
        ),
        passed_overall=passed,
        latency_ms=10.0,
    )


def test_overall_pass_rate_met():
    results = [_make_result(passed=True), _make_result(test_id="2", passed=True)]
    passed, _ = check_thresholds(results, {"overall_pass_rate": 1.0})
    assert passed


def test_overall_pass_rate_not_met():
    results = [_make_result(passed=True), _make_result(test_id="2", passed=False)]
    passed, _ = check_thresholds(results, {"overall_pass_rate": 0.8})
    assert not passed


def test_avg_score_threshold():
    results = [_make_result(score=9.0), _make_result(test_id="2", score=7.0)]
    passed, _ = check_thresholds(results, {"avg_score": 7.5})
    assert passed


def test_category_pass_rate():
    results = [
        _make_result(test_id="1", category="factual", passed=True),
        _make_result(test_id="2", category="factual", passed=False),
        _make_result(test_id="3", category="refusal", passed=True),
    ]
    passed, summary = check_thresholds(results, {"factual_pass_rate": 0.8})
    assert not passed
    assert any("FAIL" in line for line in summary)


def test_unknown_metric_reported():
    results = [_make_result()]
    passed, summary = check_thresholds(results, {"pass_rate_min": 0.5})
    # Unknown metrics should be flagged, not silently ignored
    assert any("UNKNOWN" in line and "pass_rate_min" in line for line in summary)


def test_no_thresholds():
    results = [_make_result()]
    passed, _ = check_thresholds(results, {})
    assert passed
