# Import Boundaries

## Rules
- `services/*` (pure) must not import provider SDKs or `cli/*`
- Side-effects only in adapters or CLI boundary
- `cli/standard/*` must not import `cli/dev/*`
- `workflows/*` cannot reference `dev.*` commands

## Enforcement
- Use import-linter contracts to enforce the above
- CI fails on boundary violations

## Rationale
- Preserve purity of domain logic (L2)
- Prevent provider lock-in from leaking into business code
