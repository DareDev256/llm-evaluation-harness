from typing import List, Dict, Any
from src.schemas import EvalResult
import pandas as pd

def compare_runs(baseline_results: List[EvalResult], candidate_results: List[EvalResult]) -> Dict[str, Any]:
    base_map = {r.test_id: r for r in baseline_results}
    cand_map = {r.test_id: r for r in candidate_results}
    
    regressions = []
    improvements = []
    
    # Metrics
    base_pass = sum(1 for r in baseline_results if r.passed_overall) / len(baseline_results) if baseline_results else 0
    cand_pass = sum(1 for r in candidate_results if r.passed_overall) / len(candidate_results) if candidate_results else 0
    
    base_judge_avg = sum(r.judge_result.score for r in baseline_results if r.judge_result) / len(baseline_results) if baseline_results else 0
    cand_judge_avg = sum(r.judge_result.score for r in candidate_results if r.judge_result) / len(candidate_results) if candidate_results else 0
    
    for test_id, c_res in cand_map.items():
        if test_id not in base_map:
            continue
            
        b_res = base_map[test_id]
        
        # Check for regression (Pass -> Fail)
        if b_res.passed_overall and not c_res.passed_overall:
            regressions.append({
                "test_id": test_id,
                "category": c_res.category,
                "baseline_output": b_res.output_text,
                "candidate_output": c_res.output_text,
                "reason": "Passed in baseline, failed in candidate"
            })
            
        # Check specific metrics drops (e.g. semantic score drop > 0.1)
        if b_res.semantic_score and c_res.semantic_score:
            if b_res.semantic_score - c_res.semantic_score > 0.1:
                regressions.append({
                    "test_id": test_id,
                    "category": c_res.category,
                    "reason": f"Semantic score dropped from {b_res.semantic_score:.2f} to {c_res.semantic_score:.2f}"
                })

    return {
        "metrics": {
            "baseline_pass_rate": base_pass,
            "candidate_pass_rate": cand_pass,
            "pass_rate_delta": cand_pass - base_pass,
            "baseline_judge_avg": base_judge_avg,
            "candidate_judge_avg": cand_judge_avg,
            "judge_avg_delta": cand_judge_avg - base_judge_avg
        },
        "regressions": regressions,
        "regression_count": len(regressions)
    }
