import json
import os
from typing import Optional
from src.adapters.openai_chat import OpenAIAdapter
from src.schemas import JudgeResult, AdapterConfig

# Mapping from test case category to prompt filename
_PROMPT_FILES = {
    "factual": "judge_prompt_factual.txt",
    "summary": "judge_prompt_summary.txt",
    "synthesis": "judge_prompt_synthesis.txt",
    "refusal": "judge_prompt_refusal.txt",
    "rag_grounding": "judge_prompt_rag_grounding.txt",
}

_DEFAULT_PROMPT = (
    "You are an impartial judge. Evaluate the quality of the response based on the query. "
    "Return valid JSON with: score (0-10), verdict (pass/fail), reasons (list<str>), confidence (0-1)."
)


class JudgeEvaluator:
    def __init__(self, adapter: OpenAIAdapter, prompts_dir: str = None):
        self.adapter = adapter
        if prompts_dir is None:
            self.prompts_dir = os.path.join(
                os.path.dirname(__file__), os.pardir, os.pardir, "prompts"
            )
        else:
            self.prompts_dir = prompts_dir

    def evaluate(self, query: str, output: str, category: str, expected_output: str = None) -> JudgeResult:
        system_prompt = self._get_system_prompt(category)
        user_prompt = f"Query: {query}\n\nActual Output: {output}\n\n"
        if expected_output:
            user_prompt += f"Reference Output: {expected_output}\n\n"

        user_prompt += "Provide your assessment in strict JSON format."

        response_text = self.adapter.predict(user_prompt, context=system_prompt)
        return self._parse_response(response_text)

    def _get_system_prompt(self, category: str) -> str:
        """Load the category-specific judge prompt from disk, falling back to generic then default."""
        filename = _PROMPT_FILES.get(category)
        if filename:
            path = os.path.join(self.prompts_dir, filename)
            content = self._read_prompt_file(path)
            if content:
                return content

        generic_path = os.path.join(self.prompts_dir, "judge_prompt_generic.txt")
        content = self._read_prompt_file(generic_path)
        if content:
            return content

        return _DEFAULT_PROMPT

    @staticmethod
    def _read_prompt_file(path: str) -> Optional[str]:
        """Read a prompt file, returning None if missing or empty."""
        try:
            with open(path, "r") as f:
                content = f.read().strip()
            return content if content else None
        except (FileNotFoundError, OSError):
            return None

    def _extract_json(self, text: str) -> str:
        """Extract the first top-level JSON object by matching braces."""
        start = text.find("{")
        if start == -1:
            raise ValueError("No opening brace found in text")
        depth = 0
        in_string = False
        escape_next = False
        for i in range(start, len(text)):
            ch = text[i]
            if escape_next:
                escape_next = False
                continue
            if ch == "\\":
                escape_next = True
                continue
            if ch == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        raise ValueError("No matching closing brace found")

    def _parse_response(self, text: str) -> JudgeResult:
        try:
            # Extract the first balanced JSON object
            try:
                json_str = self._extract_json(text)
                data = json.loads(json_str)
            except (ValueError, json.JSONDecodeError):
                data = json.loads(text)

            # Validate and build result with safe defaults
            verdict = data.get("verdict", "fail")
            if isinstance(verdict, str):
                verdict = verdict.lower().strip()
            if verdict not in ("pass", "fail"):
                verdict = "fail"

            try:
                return JudgeResult(
                    score=float(data.get("score", 0)),
                    verdict=verdict,
                    reasons=data.get("reasons", ["Parse error or missing reasons"]),
                    confidence=float(data.get("confidence", 0))
                )
            except Exception as e:
                return JudgeResult(
                    score=0.0,
                    verdict="fail",
                    reasons=[f"Malformed judge fields: {str(e)}", f"Raw data keys: {list(data.keys())}"],
                    confidence=0.0
                )
        except Exception as e:
            return JudgeResult(
                score=0.0,
                verdict="fail",
                reasons=[f"Failed to parse judge output: {str(e)}", f"Raw output: {text[:100]}..."],
                confidence=0.0
            )
