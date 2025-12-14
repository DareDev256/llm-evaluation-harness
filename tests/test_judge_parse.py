import pytest
from src.eval.judge import JudgeEvaluator
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
