# Duplicate Transaction Resolution Policy

## Section 1: Detection of Duplicate Transactions
A duplicate transaction occurs when multiple payment gateway webhooks or multiple bank settlement credits correspond to the same Order ID or Transaction ID.

## Section 2: Duplicate Resolution Criteria
1. Duplicate Webhooks: If two payment logs exist with identical transaction IDs and identical amounts, the system marks status as `DUPLICATE_TRANSACTION`.
2. Multiple Bank Credits: When two candidate bank credits match a single payment, the system must score and rank candidate matches based on identifier precision, date proximity, and reference string similarity.
3. If candidates cannot be differentiated with confidence ≥ 85%, the case must be marked as `UNRESOLVED` and escalated to human audit.

