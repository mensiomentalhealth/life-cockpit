# Operation Log (OpLog)

## Store (v1)
- Azure Table Storage
- PartitionKey: `<env>-<yyyymmdd>-<verb>` (avoid hot partitions)
- RowKey: `op_id`

## Fields
- `op_id`, `verb`, `actor`, `idempotency_key`, `subject_id`, `payload_hash`, `status`, `error_class`, `duration_ms`, `service_calls`, `pii_class`

## Indices
- Optional secondary table `(verb, idempotency_key)`
- Query: by `verb+date`, `subject_id`, `op_id`

## Retention
- TTL 7–30 days non-regulatory; mirror/export for regulatory retention

## Cross-links
- See `../cli-conventions.md` and `../governance/policy-as-code.md`.
