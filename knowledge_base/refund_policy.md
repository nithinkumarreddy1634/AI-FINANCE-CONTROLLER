# Refund and Chargeback Policy

## Section 1: Refund Identification
Refunds and chargeback debits appear as negative bank movements or reversed payment gateway status codes.

## Section 2: Safety Rules
The AI agent must never automatically issue refunds or execute banking transfers. It may only recommend actions such as `MARK_FOR_REVIEW` or `ESCALATE` for human finance team sign-off.

