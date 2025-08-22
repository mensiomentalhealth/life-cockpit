# Testing Strategy

## Layers
- L1 (lib): unit + contract tests with service fakes; retry/timeout behavior; error mapping
- L2 (services): pure function tests with fixtures; schema boundary tests
- L3 (cli): golden JSON outputs; exit codes; idempotency behavior; dry-run
- L4 (workflows): harness runs verb sequences with stub KV/queues; smoke tests
- E2E: minimal canaries in non-prod against sandbox tenants

## Golden tests
- Canonical JSON; stable envelopes; `GOLDEN_UPDATE=1` to refresh

## Policy tests
- Stripe requires idempotency key; Dataverse writes require `{contact_id, session_id}`
- Secrets loaded only from KV; fail inline secrets

## CI matrix
- Run suites with and without `[devcli]` extras
- Lint (ruff, mypy), workflow linter, import boundaries

## Cross-links
- See `../cli-conventions.md`, `../policy-as-code.md`, and `../operations/operation-log.md`.
