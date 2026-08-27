# Settlement Timing and Date Window Policy

## Section 1: Settlement Window Window Rules
A successful payment gateway transaction may appear in a bank or settlement record on a later date than the original customer order/payment date due to banking processing clearing cycles (T+1 to T+3 settlements).

## Section 2: Configurable Settlement Tolerance
1. Standard Settlement Window: A settlement delay of up to 3 days (72 hours) between payment date and bank credit date is considered standard operational lag and is acceptable for automated reconciliation.
2. Extended Settlement Window: A settlement delay between 4 days and 7 days may be classified as `DATE_MISMATCH` with medium confidence, requiring manual review.
3. Excessive Lag: Any transaction with settlement delay exceeding 7 days must be flagged for manual review or escalation to verify potential bank holding or processing errors.

