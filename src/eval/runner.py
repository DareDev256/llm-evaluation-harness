import time
import asyncio
from typing import List
from src.schemas import RunConfig, TestCase, EvalResult
from src.adapters import BaseAdapter
from src.adapters.mock_adapter import MockAdapter
from src.adapters.openai_chat import OpenAIAdapter
from src.adapters.http_rag import HTTPRAGAdapter
from src.eval import rules, semantic
from src.eval.judge import JudgeEvaluator
from src.utils import io

class EvalRunner:
    def __init__(self, config: RunConfig):
        self.config = config
        self.adapter = self._init_adapter(config.adapter)
        
        # Evaluators
        self.semantic_eval = semantic.SemanticEvaluator()
        
        # Judge needs OpenAI adapter usually
        # For simplicity, if adapter is mock, judge uses mock too? 
        # Requirement says judge "must be deterministic".
        # We will use OpenAIAdapter for judge if config allows, or fallback to mock if in mock mode.
        if config.adapter.type == "mock":
             self.judge = JudgeEvaluator(MockAdapter(config.adapter))
        else:
             # Judge usually uses a strong model like gpt-4
             judge_config = config.adapter.model_copy(update={"model": "gpt-4o", "temperature": 0})
             self.judge = JudgeEvaluator(OpenAIAdapter(judge_config))

    def _init_adapter(self, config) -> BaseAdapter:
        if config.type == "mock":
            return MockAdapter(config)
        elif config.type == "openai_chat":
            return OpenAIAdapter(config)
        elif config.type == "http_rag":
            return HTTPRAGAdapter(config)
        raise ValueError(f"Unknown adapter type: {config.type}")

    def run(self, test_cases_path: str, output_path: str):
        test_cases = io.read_jsonl(test_cases_path, TestCase)
        results = []
        
        print(f"Running eval on {len(test_cases)} cases...")
        
        for case in test_cases:
            res = self.evaluate_case(case)
            results.append(res)
            print(f"Evaluated {case.id}: {'PASS' if res.passed_overall else 'FAIL'}")
            
        io.write_json([r.model_dump() for r in results], output_path)
        return results

    def evaluate_case(self, case: TestCase) -> EvalResult:
        start_t = time.time()
        
        # 1. Get Prediction
        try:
            output = self.adapter.predict(case.input.query, case.input.context)
        except Exception as e:
            output = f"ERROR: {str(e)}"
            
        latency = (time.time() - start_t) * 1000
        
        # 2. Rule Checks
        rule_results = rules.evaluate_rules(output, case.expected)
        
        # 3. Semantic Similarity (if expected text provided??)
        # Requirement says "cosine similarity between embeddings of output and reference string (provide a reference if available)"
        # The Schema ExpectedOutput doesn't explicitly have a 'reference_text' field in the prompt description 
        # but user said "provide a reference if available". 
        # Let's assume one must_include string is the reference or add a field.
        # Actually, let's look at the requirements again: "must_include" etc. 
        # I'll compute similarity against the first 'must_include' if exists, as a proxy, 
        # OR I should have added a 'reference' field to ExpectedOutput. 
        # I'll stick to the strict schema requested by user:
        # { "must_include": ["..."], ... }
        # I'll join must_include as reference for now if present.
        semantic_score = 0.0
        if case.expected.must_include:
            reference = " ".join(case.expected.must_include)
            semantic_score = self.semantic_eval.compute_similarity(output, reference)
            
        # 4. Judge
        judge_result = self.judge.evaluate(
            query=case.input.query,
            output=output,
            category=case.category,
            expected_output=" ".join(case.expected.must_include) # proxy
        )
        
        # 5. Overall Pass/Fail
        # Rules must pass
        rules_passed = all(r.passed for r in rule_results)
        # Judge must pass
        judge_passed = judge_result.verdict == "pass"
        
        passed_overall = rules_passed and judge_passed
        
        return EvalResult(
            test_id=case.id,
            category=case.category,
            output_text=output,
            rule_results=rule_results,
            semantic_score=semantic_score,
            judge_result=judge_result,
            passed_overall=passed_overall,
            latency_ms=latency
        )
