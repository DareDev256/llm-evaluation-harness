from typing import List
from src.schemas import ExpectedOutput, RuleResult

def check_must_include(text: str, phrases: List[str]) -> RuleResult:
    missing = [p for p in phrases if p.lower() not in text.lower()]
    passed = len(missing) == 0
    details = f"Missing: {missing}" if missing else "All required phrases present"
    return RuleResult(rule_name="must_include", passed=passed, details=details)

def check_must_not_include(text: str, phrases: List[str]) -> RuleResult:
    present = [p for p in phrases if p.lower() in text.lower()]
    passed = len(present) == 0
    details = f"Forbidden phrases found: {present}" if present else "No forbidden phrases found"
    return RuleResult(rule_name="must_not_include", passed=passed, details=details)

def check_citations(text: str) -> RuleResult:
    # Basic check for [doc_id] or [1] style citations
    import re
    citation_pattern = r"\[\d+\]|\[doc_\d+\]"
    found = re.search(citation_pattern, text)
    passed = bool(found)
    details = "Citation found" if passed else "No valid citation found"
    return RuleResult(rule_name="citations_required", passed=passed, details=details)

def check_word_count(text: str, max_words: int) -> RuleResult:
    count = len(text.split())
    passed = count <= max_words
    details = f"Count: {count}, Max: {max_words}"
    return RuleResult(rule_name="max_words", passed=passed, details=details)

def evaluate_rules(text: str, expected: ExpectedOutput) -> List[RuleResult]:
    results = []
    
    if expected.must_include:
        results.append(check_must_include(text, expected.must_include))
        
    if expected.must_not_include:
        results.append(check_must_not_include(text, expected.must_not_include))
        
    if expected.citations_required:
        results.append(check_citations(text))
        
    if expected.max_words is not None:
        results.append(check_word_count(text, expected.max_words))
        
    return results
