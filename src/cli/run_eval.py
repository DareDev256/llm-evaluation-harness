print("DEBUG: Global scope entered")
import argparse
from src.schemas import RunConfig
from src.eval.runner import EvalRunner
from src.utils import io
import os

def main():
    print("DEBUG: Starting run_eval CLI")
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
    runner.run(args.data, args.output)
    
    print(f"Eval complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()
