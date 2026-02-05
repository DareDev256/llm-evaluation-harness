import argparse
import sys
from collections import defaultdict
from src.schemas import RunConfig
from src.eval.runner import EvalRunner
from src.utils import io
import os

def check_thresholds(results, thresholds):
    """Check results against configured thresholds. Returns (passed, summary_lines)."""
    if not thresholds:
        return True, ["No thresholds configured."]

    # Compute pass rate per category
    category_counts = defaultdict(lambda: {"total": 0, "passed": 0})
    for r in results:
        category_counts[r.category]["total"] += 1
        if r.passed_overall:
            category_counts[r.category]["passed"] += 1

    # Also compute overall pass rate
    total = len(results)
    total_passed = sum(1 for r in results if r.passed_overall)
    overall_rate = total_passed / total if total > 0 else 0.0

    all_passed = True
    summary = []

    for metric, threshold in thresholds.items():
        if metric == "overall_pass_rate":
            actual = overall_rate
        elif metric.endswith("_pass_rate"):
            # e.g. "factual_pass_rate" -> category "factual"
            category = metric.replace("_pass_rate", "")
            counts = category_counts.get(category)
            if counts and counts["total"] > 0:
                actual = counts["passed"] / counts["total"]
            else:
                actual = 0.0
        elif metric == "avg_score":
            scores = [r.judge_result.score for r in results if r.judge_result]
            actual = sum(scores) / len(scores) if scores else 0.0
        else:
            summary.append(f"  UNKNOWN  {metric}: threshold {threshold} (unrecognized metric)")
            continue

        met = actual >= threshold
        if not met:
            all_passed = False
        status = "PASS" if met else "FAIL"
        summary.append(f"  {status}  {metric}: {actual:.2%} (threshold: {threshold:.2%})")

    return all_passed, summary

def main():
    parser = argparse.ArgumentParser(description="Run LLM Evaluation")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    parser.add_argument("--data", default="data/test_cases.jsonl", help="Path to test cases JSONL")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    args = parser.parse_args()

    # Load Config
    config_dict = io.read_yaml(args.config)
    config = RunConfig.model_validate(config_dict)

    # Run
    runner = EvalRunner(config)
    results = runner.run(args.data, args.output)

    print(f"Eval complete. Results saved to {args.output}")

    # Threshold validation
    thresholds_passed, summary = check_thresholds(results, config.thresholds)
    print("\n--- Threshold Summary ---")
    for line in summary:
        print(line)

    if not thresholds_passed:
        print("\nThreshold check FAILED.")
        sys.exit(1)
    else:
        print("\nAll thresholds passed.")

if __name__ == "__main__":
    main()
