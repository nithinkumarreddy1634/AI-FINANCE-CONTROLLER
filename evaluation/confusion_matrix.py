"""
Confusion Matrix & Exception-Level Performance Generator
Generates exception-level accuracy breakdowns and confusion matrix metrics for ground-truth evaluation.
"""

import os
import sys
import json
import pandas as pd
from typing import Dict, Any, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from evaluation.run_evaluation import evaluate_systems

def generate_confusion_matrix_and_breakdown(eval_dir: str = "evaluation") -> Dict[str, Any]:
    metrics, p3_decisions = evaluate_systems(eval_dir=eval_dir)

    df = pd.DataFrame(p3_decisions)

    # Exception-level performance breakdown
    breakdown = []
    categories = df["exception_type"].unique()

    for cat in categories:
        sub = df[df["exception_type"] == cat]
        total_cases = len(sub)

        correct_cases = 0
        for _, r in sub.iterrows():
            act = r["recommended_action"]
            exp_match = r["expected_match"]
            if act == "AUTO_RECONCILE" and exp_match:
                correct_cases += 1
            elif act != "AUTO_RECONCILE" and not exp_match:
                correct_cases += 1

        accuracy = round((correct_cases / total_cases) * 100, 2)
        breakdown.append({
            "exception_type": cat,
            "total_cases": total_cases,
            "correct_cases": correct_cases,
            "accuracy_pct": accuracy
        })

    out_data = {
        "overall_metrics": metrics,
        "exception_level_breakdown": breakdown
    }

    out_file = os.path.join(eval_dir, "results", "confusion_matrix.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)

    print(f"Exception-level performance breakdown generated for {len(categories)} categories. Saved to '{out_file}'.")
    return out_data

if __name__ == "__main__":
    generate_confusion_matrix_and_breakdown()
