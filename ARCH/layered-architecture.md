# Life Cockpit Architecture

## Overview

**YOUR Personal Programmatic Life Management System**

Life Cockpit is a layered, modular Python automation framework designed to replace GUI-based workflows with script-based automation in the Microsoft 365 ecosystem. The architecture emphasizes **terminal-first verbs**, thin orchestrators, and portable backends. The system prioritizes **modularity, security, and extensibility** while evolving from temporary scaffolding to durable systems.

### Strategic Vision
- **Terminal-first verbs** are the authoritative interface: `lc <domain>.<action>`
- **Orchestrators are plumbing**: triggers, retries, routing only (no business branching)
- **Policy-as-code**: rules enforced in code (validators, linters, tests), not docs
- **Deterministic I/O**: canonical JSON, UTC timestamps, idempotent effects
- **Swap-30**: dependencies replaceable within 30 days (docs + plan)
- **Personal-first design**: built for YOUR needs, YOUR patterns, YOUR life management

---

## 🏗️ System Architecture

### Layer Map (L0–L4)
```
L0  Infra & Config (IaC)
    - Bicep/Terraform, resource lifecycles, env wiring, KV secrets, swap-30 plans
L1  Harmonized Python Shim (/lib)
    - Clients for Graph/Dataverse/Stripe; auth/retry/errors/validation/telemetry
L2  Domain Logic (/services)
    - Business rules & transforms; pure where possible; side-effects via L1 only
L3  Terminal-First CLI (/cli)
    - Stable verbs; deterministic JSON; --dry-run; idempotency; exit codes; composable
L4  Workflows (thin orchestration)
    - Triggers/schedules; fan-out/in; retries; route on exit class; never business branching
X   Cross-cutting: Policy-as-Code & Observability
    - Validators, linters, tests, structured logs/metrics/traces, audit for every effect
```

---

## Layers

### L3 Interface Layer (CLI)
- **CLI (Core)**: Primary control via Typer commands (e.g., `lc reminders.build`, `lc messages.send`)
- **Terminal (Core)**: Structured JSON/NDJSON output; deterministic by default
- **Web (Client-Facing)**: Optional dashboards; not authoritative

### L4 Orchestration Layer
- Logic Apps/Functions: triggers, retries, routing on exit class; no business branching

### L1/L2 Data & Domain Layers
- **L1**: Graph/Dataverse/Stripe adapters; mapped errors; retries/backoff
- **L2**: Pure business rules; schema-checked IO; no provider SDK imports

### Governance Layer
- Idempotency, explainability, reversibility; experiment TTL; swap-30; freedom floor

---

## 🔐 Authentication & ⚙️ Configuration
- Managed Identity → Federated Identity → KV secret chain
- Env normalization shim (`AAD_*` standard)
- Secrets from Key Vault; dev-only `.env.local` under `LC_ENV=dev`

## 📝 Observability
- JSON logs with `{op_id, verb, status, result|error, metrics}`
- Metrics: latency, success rate, retries, external call counts
- Tracing: OpenTelemetry (console dev, OTLP/LA non-dev)

## 🔄 Terminal-First Contract
- Input: stdin or `--input`; Output: JSON/NDJSON to stdout
- Exit codes: 0 OK, 10 Validation, 11 Policy, 12 Transient/Auth, 13 External, 14 Conflict
- Error envelope includes `retriable` flag and `op_id`

## Examples

### Decision → Plan → Execute
```
lc reminders.decide --date 2025-08-23 > plan.json
lc reminders.execute --input plan.json --idempotency-key "$(sha256sum plan.json)"
```

### Dev inspection (gated)
```
lc dev.dataverse.query contact --filter "statecode eq 0" --select "fullname,emailaddress1" --limit 100 --format=ndjson
```

---

## Notes
- **No business logic in orchestrators**
- **CLI verbs are primary**; `blc` is a temporary dev-only alias to be removed
- **AI layer follows the same rules** (versioned, logged, reversible)
- **Portal logic freeze**: new rules live as CLI/decision verbs
