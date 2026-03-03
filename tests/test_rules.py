import pytest
from src.eval import rules
from src.schemas import ExpectedOutput


# ── must_include ──────────────────────────────────────

def test_check_must_include_pass():
    text = "The quick brown fox"
    result = rules.check_must_include(text, ["quick", "fox"])
    assert result.passed
    assert result.rule_name == "must_include"


def test_check_must_include_fail():
    text = "The quick brown fox"
    result = rules.check_must_include(text, ["quick", "bear"])
    assert not result.passed
    assert "bear" in result.details


def test_check_must_include_case_insensitive():
    result = rules.check_must_include("Paris is the capital", ["PARIS", "capital"])
    assert result.passed


def test_check_must_include_empty_phrases():
    result = rules.check_must_include("Any text", [])
    assert result.passed


# ── must_not_include ──────────────────────────────────

def test_check_must_not_include_pass():
    text = "The quick brown fox"
    result = rules.check_must_not_include(text, ["bear", "lion"])
    assert result.passed


def test_check_must_not_include_fail():
    text = "The quick brown fox"
    result = rules.check_must_not_include(text, ["quick"])
    assert not result.passed
    assert "quick" in result.details


def test_check_must_not_include_case_insensitive():
    result = rules.check_must_not_include("Contains ERROR message", ["error"])
    assert not result.passed


# ── citations ─────────────────────────────────────────

def test_check_citations_bracket_number():
    assert rules.check_citations("Here is a fact [1].").passed


def test_check_citations_doc_id():
    assert rules.check_citations("Fact [doc_123]").passed


def test_check_citations_no_citation():
    assert not rules.check_citations("No citation here.").passed


def test_check_citations_parenthetical_not_valid():
    assert not rules.check_citations("(1) is not a bracket citation").passed


def test_check_citations_multiple():
    assert rules.check_citations("Claim [1] and [2] and [doc_5].").passed


# ── word_count ────────────────────────────────────────

def test_check_word_count_under_limit():
    assert rules.check_word_count("one two three", 5).passed


def test_check_word_count_at_limit():
    assert rules.check_word_count("one two three", 3).passed


def test_check_word_count_over_limit():
    result = rules.check_word_count("one two three", 2)
    assert not result.passed
    assert "3" in result.details  # actual count


def test_check_word_count_empty():
    assert rules.check_word_count("", 10).passed


# ── evaluate_rules integration ────────────────────────

def test_evaluate_rules_all_pass():
    expected = ExpectedOutput(
        must_include=["AI"],
        must_not_include=["Error"],
        citations_required=True,
        max_words=10,
    )
    text = "AI is great [1]."
    results = rules.evaluate_rules(text, expected)
    assert len(results) == 4
    assert all(r.passed for r in results)


def test_evaluate_rules_partial_failure():
    expected = ExpectedOutput(
        must_include=["AI"],
        must_not_include=["Error"],
        citations_required=True,
        max_words=10,
    )
    text_fail = "Error occurred."
    results = rules.evaluate_rules(text_fail, expected)
    assert not all(r.passed for r in results)


def test_evaluate_rules_no_expectations():
    """No expectations → no rules to check → empty list."""
    expected = ExpectedOutput()
    results = rules.evaluate_rules("anything", expected)
    assert results == []
