# Standard Payment Reconciliation Policy

## Section 1: Overview and Core Matching Rules
Payment reconciliation is the process of matching customer orders, payment gateway transaction webhooks, and bank settlement credits.
A transaction is considered an exact match (`MATCHED`) if and only if all three conditions are satisfied:
1. Identifier Match: The Order ID and Transaction ID correspond exactly to the bank reference string.
2. Amount Match: Expected Order Amount = Gateway Paid Amount = Bank Received Amount (within a 0.01 currency unit tolerance).
3. Status Match: Payment status is SUCCESS / COMPLETED, and Bank settlement status is SETTLED.

## Section 2: Identification Strategy
Primary matching uses strong identifiers (`order_id`, `transaction_id`, `payment_id`). Secondary matching uses fuzzy reference pattern matching and token similarity.
If strong identifiers match but amounts or dates differ, the transaction must be evaluated under specific discrepancy policies rather than declared an exact match.

