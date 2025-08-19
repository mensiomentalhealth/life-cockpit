# Principles.md

## Prime Directive
- Every capability = verb first (CLI/API), UI later.
- No business logic in views/notebooks.

## Idempotency
- All actions must be idempotent.
- Dry-run → Apply → Log → Rollback path.
- Example: PaymentQueue job run with runID, replay-safe.

## Explainability
- Every automation = explain → dry-run → apply.
- Example: AI report builder outputs rationale block before commit.

## Reversibility
- Mutations must have rollback.
- Example: Stripe payment attempt logged with reversal plan.

## Patterns
- **Experiment TTL**: Default 30 days. Archive on expiry unless promoted.
- **Dependency Swap-30**: No dependency that can’t be swapped in ≤30 days. Living swap plan for each critical dep.
- **HITL Matrix**: Risk-based approvals gate dangerous actions.
- **Freedom Floor**: Human override always possible.

## Example: Reminder System v1
- Dry-run shows queued reminders.
- Apply sends email.
- Log saved in Action Log.
- Rollback = cancel unsent queue.

## Example: Client Report Automation v1
- AI generates draft.
- Human approves (HITL).
- Commit → DV rich text.
- Rollback = delete draft.

## Notes
- Principles apply across OPS, PM, and DELI.
- Revisit monthly during cadence review.