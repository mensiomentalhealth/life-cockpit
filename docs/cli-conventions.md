# CLI Conventions (Authoritative)

## Surfaces (three)
- Standard (authoritative): `lc <domain>.<action>[@vN]`
  - Business verbs, storage-agnostic. Allowed in workflows.
- Sys (prod-safe ops): `lc sys.<action>`
  - Read/health/peek via ports; no direct provider access.
- Dev plumbing (gated): `lc dev.<provider>.<action>`
  - Provider-specific inspection/tools (Dataverse, Graph, Stripe). Never used in workflows; gated by build+env.

## Naming
- Verb form: `lc reminders.build@v1`, `lc messages.send@v1`, `lc payments.capture@v1`
- Versioning: breaking schema changes → new `@vN`; keep `@v1` default during grace period with deprecation notice.

## Flags (stable set)
- `--input/-i <path|->`: JSON input (default `-` stdin)
- `--output/-o <path|->`: destination (default `-` stdout)
- `--format json|ndjson`: default `json` (dev list verbs may default `ndjson`)
- `--dry-run`: no side-effects; still validate and plan
- `--idempotency-key <str>`: overrides default key
- `--since <iso8601>`: incremental fetch (verbs that support it)
- `--select <cols>`: comma-separated projection (verbs that support it)
- `--limit <n>`: cap results (verbs that stream/list)
- `--page-size <n>`: provider pagination hint (only where relevant)
- `--concurrency <n>`: bounded parallelism (only where relevant)
- `--require`: flips NotFound from OK to ValidationError for existence-dependent reads

## Deterministic I/O
- Canonical JSON only: sorted keys, UTC `Z` timestamps, Decimal for money (serialized as string).
- Use a single `dump_json()`/`load_json()`; never call `json.dumps` directly.

## Envelopes and streaming
- `format=json`: single envelope to stdout: `{op_id, verb, status: "ok"|"error", result|error, metrics, warnings}`
- `format=ndjson` (list verbs): stream records to stdout; write a footer to stderr: `{op_id, status, metrics}`

## Exit codes
- 0 OK
- 10 ValidationError (non‑retriable)
- 11 PolicyError (operator fix required)
- 12 TransientError/AuthError (retriable)
- 13 ExternalServiceError (often retriable; see envelope.retriable)
- 14 Conflict (idempotent no‑op / version conflict)
- NotFound: 0 for reads, 10 if `--require`

## Idempotency
- Scope per verb: `subject_scope` (e.g., contact/session) + canonical payload hash.
- Default key = `sha256(canonical_payload + verb + subject_scope)`.
- TTLs: 48h (payments), 7d (messaging), 24h (metadata writes).
- Operation Log records `{op_id, idempotency_key, payload_hash, effect_summary}`.

## Workflow rules
- Allowed: chain standard verbs (and `sys.*`) with triggers, retries, and routing on exit class.
- Disallowed: any `dev.*` invocation; any business branching in workflows (enforced by linter).

## Dev surface gating
- Build-time: dev CLI in optional extra (`[devcli]`); prod images don’t install it.
- Runtime: require `LC_ENABLE_DEV_CLI=1` and `LC_ENV in {dev,stage}`; block in `prod`.
- Writes: require `--force` and `--reason`; block in `prod`.

## Examples
- Standard:
  - `lc reminders.decide@v1 --input - --output plan.json`
  - `lc reminders.execute@v1 --input plan.json --idempotency-key "$(sha256sum plan.json)"`
- Sys (ports-backed):
  - `lc sys.health`
  - `lc sys.peek.sessions --id abc123 --require`
- Dev (gated):
  - `lc dev.dataverse.query contact --filter "statecode eq 0" --select "fullname,email" --limit 100 --format=ndjson`
  - `lc dev.dataverse.update contact 0000-... --input payload.json --dry-run` (requires `--force` to apply)

## Deprecation
- `blc dv:*` → `lc dev.dataverse.*` (dev-only alias). Show warning until removal.
