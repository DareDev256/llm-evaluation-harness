import pytest
from pydantic import ValidationError
from src.schemas import (
    TestCase, TestInput, ExpectedOutput,
    EvalResult, JudgeResult, RuleResult,
    AdapterConfig, RunConfig,
)


# ── TestCase validation ───────────────────────────────

def test_test_case_valid():
    tc = TestCase(
        id="test_1",
        category="factual",
        input=TestInput(query="What is AI?"),
        expected=ExpectedOutput(must_include=["artificial"]),
    )
    assert tc.id == "test_1"
    assert tc.category == "factual"


def test_test_case_invalid_category():
    with pytest.raises(ValidationError):
        TestCase(
            id="test_1",
            category="invalid_category",
            input=TestInput(query="test"),
            expected=ExpectedOutput(),
        )


def test_expected_output_defaults():
    exp = ExpectedOutput()
    assert exp.must_include == []
    assert exp.must_not_include == []
    assert exp.citations_required is False
    assert exp.max_words is None
    assert exp.refusal_ok is False


# ── AdapterConfig ─────────────────────────────────────

def test_adapter_config_defaults():
    cfg = AdapterConfig(type="mock")
    assert cfg.model == "gpt-4o-mini"
    assert cfg.temperature == 0.0
    assert cfg.max_tokens == 500


def test_adapter_config_invalid_type():
    with pytest.raises(ValidationError):
        AdapterConfig(type="invalid_adapter")


# ── RunConfig ─────────────────────────────────────────

def test_run_config_defaults():
    cfg = RunConfig(adapter=AdapterConfig(type="mock"))
    assert cfg.thresholds == {}
    assert cfg.enable_semantic is True


# ── EvalResult ────────────────────────────────────────

def test_eval_result_construction():
    result = EvalResult(
        test_id="1",
        category="factual",
        output_text="Paris",
        rule_results=[RuleResult(rule_name="must_include", passed=True, details="ok")],
        semantic_score=0.95,
        judge_result=JudgeResult(score=9.0, verdict="pass", reasons=["Correct"], confidence=0.9),
        passed_overall=True,
        latency_ms=12.5,
    )
    assert result.passed_overall
    assert result.judge_result.score == 9.0
