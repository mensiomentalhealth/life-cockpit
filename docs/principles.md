# Principles.md

## Prime Directive
- Every capability = verb first (CLI/API), UI later.
- No business logic in views/notebooks.
- **Personal-first design**: Built for YOUR needs, YOUR patterns, YOUR life management.

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

## Personal Life Management
- **YOUR System**: Designed around YOUR needs, YOUR patterns, YOUR goals
- **YOUR Data**: Your client data, your business processes, your life organization
- **YOUR Control**: You decide what gets automated, what gets logged, what gets shared
- **YOUR Growth**: Scalable systems that grow with YOUR business and life

## Patterns
- **Experiment TTL**: Default 30 days. Archive on expiry unless promoted.
- **Dependency Swap-30**: No dependency that can't be swapped in ≤30 days. Living swap plan for each critical dep.
- **HITL Matrix**: Risk-based approvals gate dangerous actions.
- **Freedom Floor**: Human override always possible.
- **Personal Workflow**: YOUR daily patterns, YOUR business processes, YOUR life rhythms

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

## Example: YOUR Daily Life Management
- Morning startup sequence for YOUR day
- Client session management for YOUR practice
- Communication automation for YOUR clients
- Evening shutdown for YOUR peace of mind

## Notes
- Principles apply across YOUR operations, project management, and deliverables
- Revisit monthly during cadence review
- **This is YOUR system for YOUR life**