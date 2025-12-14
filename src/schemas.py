from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field

class TestInput(BaseModel):
    query: str
    context: Optional[str] = None

class ExpectedOutput(BaseModel):
    must_include: List[str] = Field(default_factory=list)
    must_not_include: List[str] = Field(default_factory=list)
    citations_required: bool = False
    max_words: Optional[int] = None
    refusal_ok: bool = False

class TestCase(BaseModel):
    id: str
    category: Literal["factual", "summary", "synthesis", "refusal", "rag_grounding"]
    input: TestInput
    expected: ExpectedOutput

class RuleResult(BaseModel):
    rule_name: str
    passed: bool
    details: str

class JudgeResult(BaseModel):
    score: float
    verdict: Literal["pass", "fail"]
    reasons: List[str]
    confidence: float

class EvalResult(BaseModel):
    test_id: str
    category: str
    output_text: str
    rule_results: List[RuleResult]
    semantic_score: Optional[float] = None
    judge_result: Optional[JudgeResult] = None
    passed_overall: bool
    latency_ms: float

class AdapterConfig(BaseModel):
    type: Literal["openai_chat", "http_rag", "mock"]
    model: str = "gpt-4o-mini"
    prompt_template_path: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 500
    base_url: Optional[str] = None
    timeout: int = 30
    retries: int = 1

class RunConfig(BaseModel):
    adapter: AdapterConfig
    thresholds: Dict[str, float] = Field(default_factory=dict)
