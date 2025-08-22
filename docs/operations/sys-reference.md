# System Operations (sys.*) Reference

## Purpose
`lc sys.*` provides provider-agnostic, production-safe operational verbs. These read through L2 ports and health adapters, not raw provider SDKs.

## Principles
- Read-only by default; no direct writes
- Safe in prod; allowed in workflows
- No provider lock-in; routes through domain ports

## Examples
- `lc sys.health` — health check across adapters
- `lc sys.peek.sessions --id <session_id> --require` — read via ports (NotFound→10 with --require)
- `lc sys.search --entity session --query "..."` — domain search through ports

## Differences vs dev.*
- `sys.*` is provider-agnostic and prod-safe; `dev.*` is provider-specific, gated, never used in workflows.

## Workflow usage
- Allowed to route on exit class; no business branching.

## Cross-links
- See `../cli-conventions.md` for CLI contract.
- See `../workflow-guidelines.md` for workflow rules.
