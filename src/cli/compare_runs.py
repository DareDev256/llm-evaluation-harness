import argparse
from src.schemas import EvalResult
from src.eval import compare, reporting
from src.utils import io

def main():
    parser = argparse.ArgumentParser(description="Compare Eval Runs")
    parser.add_argument("--baseline", required=True, help="Path to baseline results JSON")
    parser.add_argument("--candidate", required=True, help="Path to candidate results JSON")
    parser.add_argument("--output-dir", default="reports", help="Directory to save comparison reports")
    args = parser.parse_args()
    
    # Load Results
    # Load Results
    import json
    with open(args.baseline, 'r') as f:
        base_data = json.load(f)
        base_results = [EvalResult.model_validate(x) for x in base_data]
        
    with open(args.candidate, 'r') as f:
        cand_data = json.load(f)
        cand_results = [EvalResult.model_validate(x) for x in cand_data]

    # Compare
    comparison = compare.compare_runs(base_results, cand_results)
    
    # Report
    reporting.save_report(comparison, args.output_dir)
    print(f"Comparison complete. Reports saved to {args.output_dir}")

if __name__ == "__main__":
    main()
