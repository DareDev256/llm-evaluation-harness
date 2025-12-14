import pytest
from src.eval import rules
from src.schemas import ExpectedOutput

def test_check_must_include():
    text = "The quick brown fox"
    # Pass
    result = rules.check_must_include(text, ["quick", "fox"])
    assert result.passed
    assert result.rule_name == "must_include"
    
    # Fail
    result = rules.check_must_include(text, ["quick", "bear"])
    assert not result.passed
    assert "bear" in result.details

def test_check_must_not_include():
    text = "The quick brown fox"
    # Pass
    result = rules.check_must_not_include(text, ["bear", "lion"])
    assert result.passed
    
    # Fail
    result = rules.check_must_not_include(text, ["quick"])
    assert not result.passed
    assert "quick" in result.details

def test_check_citations():
    # Pass - bracket style
    assert rules.check_citations("Here is a fact [1].").passed
    assert rules.check_citations("Fact [doc_123]").passed
    
    # Fail
    assert not rules.check_citations("No citation here.").passed
    assert not rules.check_citations("(1) is not a bracket citation").passed

def test_check_word_count():
    text = "one two three"
    assert rules.check_word_count(text, 5).passed
    assert rules.check_word_count(text, 3).passed
    assert not rules.check_word_count(text, 2).passed

def test_evaluate_rules_integration():
    expected = ExpectedOutput(
        must_include=["AI"],
        must_not_include=["Error"],
        citations_required=True,
        max_words=10
    )
    text = "AI is great [1]."
    results = rules.evaluate_rules(text, expected)
    
    assert len(results) == 4
    assert all(r.passed for r in results)
    
    # Test failure case
    text_fail = "Error occurred."
    results_fail = rules.evaluate_rules(text_fail, expected)
    assert not all(r.passed for r in results_fail)
