"""
Unit tests for ConfidenceScorer calculations.
"""

from reconciliation import ConfidenceScorer, ReconciliationStatus, ScoringConfig

def test_confidence_scorer_matched():
    scorer = ConfidenceScorer()
    score, reasons = scorer.calculate_score(ReconciliationStatus.MATCHED, 1000.0, 1000.0, 1000.0)
    assert score == 100.0
    assert len(reasons) > 0

def test_confidence_scorer_penalties():
    scorer = ConfidenceScorer()
    score_missing, _ = scorer.calculate_score(ReconciliationStatus.MISSING_PAYMENT, 1000.0, None, None)
    assert score_missing < 30.0

    score_amt, _ = scorer.calculate_score(ReconciliationStatus.AMOUNT_MISMATCH, 1000.0, 1000.0, 900.0)
    assert score_amt <= 50.0

def test_custom_scoring_config():
    custom_cfg = ScoringConfig(matched_base=100.0, reference_mismatch_penalty=40.0)
    scorer = ConfidenceScorer(config=custom_cfg)
    score, _ = scorer.calculate_score(ReconciliationStatus.REFERENCE_MISMATCH, 1000.0, 1000.0, 1000.0)
    assert score == 60.0

