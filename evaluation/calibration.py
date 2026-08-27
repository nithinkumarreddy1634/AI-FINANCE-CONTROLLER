"""
Confidence Calibration & Threshold Optimization Module
Analyzes AI confidence ranges (90-100, 80-89, 70-79, 60-69, <60) vs actual accuracy.
Grid-searches optimal auto-reconciliation and human-review thresholds prioritizing financial safety.
"""

import os
import sys
import json
import pandas as pd
from typing import Dict, Any, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from evaluation.run_evaluation import evaluate_systems

def analyze_calibration_and_optimize_thresholds(eval_dir: str = "evaluation") -> Dict[str, Any]:
    _, p3_decisions = evaluate_systems(eval_dir=eval_dir)
    df = pd.DataFrame(p3_decisions)

    # 1. Confidence Calibration Buckets
    buckets = {
        "90–100": {"min": 90.0, "max": 100.0, "count": 0, "correct": 0},
        "80–89": {"min": 80.0, "max": 89.99, "count": 0, "correct": 0},
        "70–79": {"min": 70.0, "max": 79.99, "count": 0, "correct": 0},
        "60–69": {"min": 60.0, "max": 69.99, "count": 0, "correct": 0},
        "Below 60": {"min": 0.0, "max": 59.99, "count": 0, "correct": 0}
    }

    for _, r in df.iterrows():
        conf = r["confidence"]
        act = r["recommended_action"]
        exp_match = r["expected_match"]
        is_correct = (act == "AUTO_RECONCILE" and exp_match) or (act != "AUTO_RECONCILE" and not exp_match)

        for b_name, b_info in buckets.items():
            if b_info["min"] <= conf <= b_info["max"]:
                b_info["count"] += 1
                if is_correct:
                    b_info["correct"] += 1
                break

    calibration_results = []
    for b_name, b_info in buckets.items():
        cnt = b_info["count"]
        corr = b_info["correct"]
        acc = round((corr / max(cnt, 1)) * 100, 2) if cnt > 0 else 0.0
        calibration_results.append({
            "confidence_range": b_name,
            "total_predictions": cnt,
            "correct_predictions": corr,
            "actual_accuracy_pct": acc
        })

    # 2. Threshold Optimization Grid Search
    auto_thresholds = [85, 90, 92, 95]
    review_thresholds = [60, 65, 70, 75]

    grid_results = []
    best_config = None
    min_false_matches = 999999

    for auto_t in auto_thresholds:
        for rev_t in review_thresholds:
            if rev_t >= auto_t:
                continue

            auto_count = 0
            review_count = 0
            escalate_count = 0
            false_matches = 0
            correct = 0

            for _, r in df.iterrows():
                conf = r["confidence"]
                exp_match = r["expected_match"]

                # Apply test thresholds
                if conf >= auto_t:
                    action = "AUTO_RECONCILE"
                    auto_count += 1
                    if exp_match:
                        correct += 1
                    else:
                        false_matches += 1
                elif conf >= rev_t:
                    action = "MARK_FOR_REVIEW"
                    review_count += 1
                    if not exp_match:
                        correct += 1
                else:
                    action = "ESCALATE"
                    escalate_count += 1
                    if not exp_match:
                        correct += 1

            false_match_rate = round((false_matches / len(df)) * 100, 2)
            accuracy = round((correct / len(df)) * 100, 2)

            res = {
                "auto_reconcile_threshold": auto_t,
                "human_review_threshold": rev_t,
                "auto_count": auto_count,
                "review_count": review_count,
                "escalate_count": escalate_count,
                "false_matches": false_matches,
                "false_match_rate_pct": false_match_rate,
                "accuracy_pct": accuracy
            }
            grid_results.append(res)

            if false_matches < min_false_matches:
                min_false_matches = false_matches
                best_config = res

    output_data = {
        "calibration_analysis": calibration_results,
        "recommended_optimal_thresholds": best_config,
        "threshold_grid_search": grid_results
    }

    out_file = os.path.join(eval_dir, "results", "calibration.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Confidence calibration and threshold optimization completed. Best config: Auto {best_config['auto_reconcile_threshold']}%, Review {best_config['human_review_threshold']}%. Saved to '{out_file}'.")
    return output_data

if __name__ == "__main__":
    analyze_calibration_and_optimize_thresholds()
