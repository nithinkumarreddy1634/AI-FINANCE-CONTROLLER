# Partial Payment and Shortfall Policy

## Section 1: Shortfall Handling
When the amount received in bank settlement or paid at gateway is less than the expected order total, the system must classify the record as `PARTIAL_PAYMENT` or `PARTIAL_MATCH`.

## Section 2: Partial Reconciliation Rules
1. Small Variance / Gateway Commission Deduction: If the received amount is within 1% to 5% of expected order amount, the variance is likely a payment gateway processing fee deduction. It should be flagged as `MARK_FOR_REVIEW` for fee accounting entry creation.
2. Major Partial Shortfall: If received amount is significantly less (e.g. 50% partial payment), the order balance remains outstanding. The AI agent must recommend `MARK_FOR_REVIEW` and prevent automatic full order resolution.
3. Overpayment: If received amount exceeds expected amount, the excess must be logged for refund or customer credit credit entry.

