import os
import pytest
from src.eval.judge import JudgeEvaluator, _PROMPT_FILES, _DEFAULT_PROMPT
from src.schemas import AdapterConfig
from src.adapters.openai_chat import OpenAIAdapter
from unittest.mock import MagicMock

class MockOpenAIAdapter(OpenAIAdapter):
    def __init__(self):
        pass # Skip init that requires key
    def predict(self, query, context=None):
        return ""

def test_parse_response_valid():
    judge = JudgeEvaluator(MockOpenAIAdapter())
    json_text = '{"score": 9.5, "verdict": "pass", "reasons": ["Good"], "confidence": 0.9}'
    result = judge._parse_response(json_text)
    assert result.score == 9.5
    assert result.verdict == "pass"
    assert result.reasons == ["Good"]

def test_parse_response_with_markdown():
    judge = JudgeEvaluator(MockOpenAIAdapter())
    text = 'Here is the json:\n```json\n{"score": 5, "verdict": "fail", "reasons": ["Bad"], "confidence": 0.8}\n```'
    result = judge._parse_response(text)
    assert result.score == 5.0
    assert result.verdict == "fail"

def test_parse_response_invalid():
    judge = JudgeEvaluator(MockOpenAIAdapter())
    text = "Not a json"
    result = judge._parse_response(text)
    assert result.score == 0.0
    assert result.verdict == "fail"
    assert "Failed to parse" in result.reasons[0]


# --- Judge prompt loading tests ---

def test_get_system_prompt_loads_factual_file():
    """Judge should load the factual rubric from prompts/ directory."""
    judge = JudgeEvaluator(MockOpenAIAdapter())
    prompt = judge._get_system_prompt("factual")
    # The real prompt file contains detailed scoring criteria
    assert "factual accuracy" in prompt.lower()
    assert "9-10" in prompt
    assert prompt != _DEFAULT_PROMPT

def test_get_system_prompt_loads_refusal_file():
    """Judge should load the refusal rubric from prompts/ directory."""
    judge = JudgeEvaluator(MockOpenAIAdapter())
    prompt = judge._get_system_prompt("refusal")
    assert "refus" in prompt.lower()
    assert "9-10" in prompt

def test_get_system_prompt_loads_all_categories():
    """Every mapped category should resolve to a non-default prompt."""
    judge = JudgeEvaluator(MockOpenAIAdapter())
    for category in _PROMPT_FILES:
        prompt = judge._get_system_prompt(category)
        assert prompt != _DEFAULT_PROMPT, f"Category '{category}' fell back to default prompt"
        assert len(prompt) > 100, f"Category '{category}' prompt suspiciously short"

def test_get_system_prompt_unknown_category_falls_back():
    """Unknown category should fall back to generic prompt file."""
    judge = JudgeEvaluator(MockOpenAIAdapter())
    prompt = judge._get_system_prompt("unknown_category_xyz")
    # Should get the generic prompt file content, not the hardcoded default
    assert "impartial judge" in prompt.lower()

def test_get_system_prompt_missing_dir_falls_back_to_default():
    """If prompts_dir doesn't exist, should fall back to _DEFAULT_PROMPT."""
    judge = JudgeEvaluator(MockOpenAIAdapter(), prompts_dir="/nonexistent/path")
    prompt = judge._get_system_prompt("factual")
    assert prompt == _DEFAULT_PROMPT
