# Policy as Code

## Runtime validators
- Stripe calls require `idempotency_key` → PolicyError 11 if missing
- Dataverse writes require `{contact_id, session_id}` tags → PolicyError 11
- Secrets must be KV-sourced; fail startup on inline secret detection
- Env normalization: `AAD_*` standard; loader maps to `AZURE_*` for compatibility

## Build/Test gates
- CLI golden-file tests (deterministic JSON)
- Schema regression tests (Pydantic v2 → JSON Schema)
- Policy hook tests (missing idempotency/tags)

## Static/Lint
- Workflow linter: allow exit-class routing, ban business branching and any `dev.*`
- Import boundaries (import-linter): enforce purity and no `cli/dev` imports
- CI matrix: run tests with and without `[devcli]` extras

## IaC guardrails (summary)
- KV references enforced; deny public endpoints unless allowed; resource tags; swap‑30 docs

## Cross-links
- See `../workflow-guidelines.md` for orchestrator rules.
- See `../development/testing-strategy.md` for golden tests and harness.
