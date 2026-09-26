"""
Automated Ground-Truth Evaluation Test (500 Records)
"""

from evaluation.run_evaluation import evaluate_systems

def test_ground_truth_evaluation_metrics():
    metrics, p3_decisions = evaluate_systems()

    assert metrics["total_records_evaluated"] == 500
    p3_metrics = metrics["phase3_ai_rag"]

    # Financial Safety Assertions
    assert p3_metrics["accuracy_pct"] >= 80.0
    assert p3_metrics["false_match_rate_pct"] <= 10.0
    assert len(p3_decisions) == 500

