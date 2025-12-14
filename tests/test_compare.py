import pytest
from src.eval.compare import compare_runs
from src.schemas import EvalResult, JudgeResult

def make_result(id="1", passed=True, score=10.0, output="A"):
    return EvalResult(
        test_id=id,
        category="cat",
        output_text=output,
        rule_results=[],
        semantic_score=1.0,
        judge_result=JudgeResult(score=score, verdict="pass" if passed else "fail", reasons=[], confidence=1.0),
        passed_overall=passed,
        latency_ms=10.0
    )

def test_compare_runs_no_regression():
    base = [make_result(id="1", passed=True)]
    cand = [make_result(id="1", passed=True)]
    res = compare_runs(base, cand)
    assert res["regression_count"] == 0
    assert res["metrics"]["pass_rate_delta"] == 0.0

def test_compare_runs_regression():
    base = [make_result(id="1", passed=True)]
    cand = [make_result(id="1", passed=False)]
    res = compare_runs(base, cand)
    assert res["regression_count"] == 1
    assert res["regressions"][0]["test_id"] == "1"
