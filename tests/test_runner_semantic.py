import pytest
from src.eval.runner import EvalRunner
from src.schemas import RunConfig, AdapterConfig, TestCase, TestInput, ExpectedOutput


def test_eval_runner_skips_semantic_when_disabled(monkeypatch):
    # If semantic is disabled in config, the heavy evaluator should not be constructed.
    def fail_semantic(*args, **kwargs):
        raise AssertionError("SemanticEvaluator should not be constructed when enable_semantic is False")

    monkeypatch.setattr("src.eval.runner.semantic.SemanticEvaluator", fail_semantic)

    config = RunConfig(adapter=AdapterConfig(type="mock"), thresholds={}, enable_semantic=False)
    runner = EvalRunner(config)

    case = TestCase(
        id="smoke",
        category="factual",
        input=TestInput(query="What is the capital of France?"),
        expected=ExpectedOutput(must_include=["Paris"], citations_required=True),
    )

    result = runner.evaluate_case(case)

    assert runner.semantic_eval is None
    assert result.semantic_score == 0.0
