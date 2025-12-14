from typing import List, Dict
from src.schemas import EvalResult
import pandas as pd
import json

def generate_summary_md(metrics: Dict, regressions: List[Dict]) -> str:
    md = "# Evaluation Report\n\n"
    
    md += "## Overall Metrics\n"
    md += "| Metric | Baseline | Candidate | Delta |\n"
    md += "|--------|----------|-----------|-------|\n"
    md += f"| Pass Rate | {metrics['baseline_pass_rate']:.2%} | {metrics['candidate_pass_rate']:.2%} | {metrics['pass_rate_delta']:.2%} |\n"
    md += f"| Judge Score | {metrics['baseline_judge_avg']:.2f} | {metrics['candidate_judge_avg']:.2f} | {metrics['judge_avg_delta']:.2f} |\n"
    
    md += "\n## Regressions\n"
    if not regressions:
        md += "No regressions detected.\n"
    else:
        for reg in regressions:
            md += f"### Test {reg['test_id']} ({reg.get('category', 'unknown')})\n"
            md += f"- Reason: {reg['reason']}\n"
            if 'baseline_output' in reg:
                md += f"- **Baseline**: {reg['baseline_output'][:100]}...\n"
                md += f"- **Candidate**: {reg['candidate_output'][:100]}...\n"
            md += "\n"
            
    return md

def save_report(comparison: Dict, output_dir: str = "reports"):
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Save diff.json
    with open(f"{output_dir}/diff.json", "w") as f:
        json.dump(comparison, f, indent=2)
        
    # Save summary.md
    md = generate_summary_md(comparison["metrics"], comparison["regressions"])
    with open(f"{output_dir}/summary.md", "w") as f:
        f.write(md)
        
    # Save metrics.csv
    # Flatten metrics to single row dataframe
    metrics = comparison["metrics"]
    df = pd.DataFrame([metrics])
    df.to_csv(f"{output_dir}/metrics.csv", index=False)
