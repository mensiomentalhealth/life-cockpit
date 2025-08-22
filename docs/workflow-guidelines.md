# Workflow Guidelines (Allowed vs Disallowed)

## Philosophy
- Orchestrators are thin plumbing: triggers, schedules, fan‑out/in, retries, routing on exit class.
- Business branching (who/what/when) belongs in decision verbs, not in workflow JSON.

## Allowed in Workflows
- Triggers/schedules
- Platform retries/backoff with jitter
- Fan‑out/fan‑in
- Switch on exit class: success | transient | validation
- Dead‑letter and observability hooks
- Calling standard verbs: `lc <domain>.<action>`
- Calling sys verbs: `lc sys.*`

## Disallowed in Workflows
- Any branching on domain fields (pricing, thresholds, routing, per‑tenant exceptions)
- Any use of `lc dev.*` commands
- Business logic in workflow JSON
- Direct provider API calls

## Pattern: Decision → Plan → Execute
```bash
lc reminders.decide --date 2025-08-23 > plan.json
lc reminders.execute --input plan.json
```

## Linter Rules (Policy-as-Code)
- Forbid `Switch`/`Condition` on domain payload fields; allow only exit-class based routing
- Ban any `command` or `args` containing `"dev."`
- Maintain allowlist of approved connectors/patterns
- Fail PR if business fields appear in workflow decision nodes

## Workflow Testing
- Local harness executes verb sequences with stub KV/queues
- Simulate retries/backoff
- Assert only exit-class routing happens

## Cross-links
- See [CLI Conventions](cli-conventions.md) for CLI contract and envelopes
- See [Policy as Code](governance/policy-as-code.md) for linter implementation and CI gates
- See [Error Taxonomy](operations/error-taxonomy.md) for exit codes and retry semantics
