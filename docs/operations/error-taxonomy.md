# Error Taxonomy and Exit Codes

## Classes → Exit Codes
- ValidationError → 10 (non‑retriable)
- PolicyError → 11 (operator fix)
- TransientError → 12 (retriable)
- AuthError → 12 (retriable when refresh may succeed)
- ExternalServiceError → 13 (often retriable; see `retriable`)
- ConflictError → 14 (idempotent no‑op/version conflict)
- NotFound → 0 for reads; 10 if required for write path or `--require`

## Retry semantics
- Each error includes `is_transient: bool`
- `AuthError` transient only when MI/refresh plausible; otherwise PolicyError

## JSON error envelope
```
{"op_id":"...","verb":"reminders.execute@v1","status":"error","error":{"error_class":"ValidationError","message":"...","retriable":false},"metrics":{"duration_ms":1234}}
```

## Operator guidance
- Exit 12/13 with `retriable=true` → retry
- Exit 10/11/14 → no retry; human or idempotent handling

## Cross-links
- See `operation-log.md` and `../cli-conventions.md`.
