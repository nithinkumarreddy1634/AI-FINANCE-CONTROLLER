# Manual Review Routing Policy

## Section 1: Medium Confidence Routing
Any transaction with confidence score between 70% and 89% or containing ambiguous formatting variations (such as reference typos or minor fee variances) must be assigned recommended action `MARK_FOR_REVIEW`.

## Section 2: Audit Form Requirements
Human reviewers must inspect transaction evidence, AI reasoning, and policy citations before submitting an `APPROVED`, `REJECTED`, or `MODIFIED` sign-off with an explanatory audit note.

