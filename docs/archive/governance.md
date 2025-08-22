# Governance & Compliance Packaging

## Permissions Manifest

- Azure AD Application (Service Principal)
  - AAD_CLIENT_ID: configured
  - AAD_TENANT_ID: configured
  - API scopes: Dataverse `/.default`
- Dataverse Environment
  - App user added to environment
  - Roles: Basic User (min), System Customizer (custom entities), System Administrator (admin only)
- Impersonation
  - MSCRMCallerID used only when --as-user provided
  - Requires Dataverse role: Act on Behalf of Another User

## Data Touchpoints (Dataverse)

- Entities (logical -> set):
  - account -> accounts (read; optional write for business ops)
  - contact -> contacts (read)
  - cre92_scheduledmessage -> cre92_scheduledmessages (read; write by messaging processor)
  - annotations -> annotations (create for notes)
- Fields commonly accessed:
  - account: name, accountid
  - contact: fullname, emailaddress1, contactid
  - cre92_scheduledmessage: cre92_messageidentifier, cre92_messagestatus, createdon

## Operational Controls

- Read-only by default in CLI
- Write verbs require explicit command (create, update, delete, note)
- Retry with exponential backoff; circuit breaker to fail fast on sustained errors
- Structured logging: attempts, latency, status codes
 - Guardrails: `safe_operation` decorator enforces dry-run defaults and approval; wrapper returns `{success, dry_run, result, run_id}`

## Monitoring

- Application Insights (recommended)
  - Track dv_call_success, dv_call_transient_error, dv_call_5xx, dv_call_retry, dv_call_failed
  - Track circuit transitions: dv_circuit_open, dv_circuit_half_open, dv_circuit_closed
