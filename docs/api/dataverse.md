# Dataverse Module API

The `dataverse` module provides a synchronous, terminal-first dev layer for the Dataverse Web API with proper OData semantics, optional impersonation, retries, connection pooling, and a circuit breaker.

## 📚 Overview

- Auth via Azure AD application using client credentials
- Entity metadata: resolve logical name → `EntitySetName`
- CRUD primitives (sync) with `$filter`, `$select`, `$top`
- Optional impersonation via `MSCRMCallerID`
- Resilience: exponential backoff retries + circuit breaker

## 🔧 Dev Layer (sync) and CLI

### Dev Layer Functions (sync)
- `whoami(impersonate: str|None=None) -> dict`
- `entity_def(logical_name: str) -> dict  # {EntitySetName, PrimaryIdAttribute, PrimaryNameAttribute}`
- `entity_set(logical_name: str) -> str`
- `get(entity_set: str, id: str, select: str|None=None, expand: str|None=None) -> dict`
- `query(entity_set: str, filter: str="", select: str="", top: int=10) -> dict  # may include @odata.count`
- `create(entity_set: str, payload: dict, *, impersonate: str|None=None) -> dict`
- `update(entity_set: str, id: str, payload: dict, *, impersonate: str|None=None) -> None`
- `delete(entity_set: str, id: str, *, impersonate: str|None=None) -> None`
- `create_note(regarding_entity_set: str, regarding_id: str, subject: str, notetext: str, *, impersonate: str|None=None) -> dict`
- `find_user_systemuserid(upn_or_domainname: str) -> str`
- `probe() -> dict  # token, whoami, metadata`

### CLI Verbs (alias: `dv`)

```bash
# Probe and identity
python blc.py dataverse probe
python blc.py dataverse whoami [--as-user <systemuserid>]

# Metadata
python blc.py dataverse entity-def <logical_name>

# Records
python blc.py dataverse get <logical_name> <guid> [--select "..."] [--expand "..."]
python blc.py dataverse query <logical_name> [--filter "..."] [--select "..."] [--top 20]

# Writes (explicit only)
python blc.py dataverse create <logical_name> --data-file payload.json [--as-user <systemuserid>]
python blc.py dataverse update <logical_name> <guid> --data-file payload.json [--as-user <systemuserid>]
python blc.py dataverse delete <logical_name> <guid> [--as-user <systemuserid>]
python blc.py dataverse note <logical_name> <guid> --subject "..." --body-file note.md [--as-user <systemuserid>]
```

## 🔐 Authentication (AAD)

### Token Acquisition

```python
from dataverse.auth import dv_token

token = dv_token()  # Uses AAD_* env vars and DATAVERSE_URL
```

### Required Environment Variables

```bash
# Dataverse
DATAVERSE_URL=https://your-org.crm.dynamics.com

# Azure AD (AAD)
AAD_CLIENT_ID=your_client_id_here
AAD_CLIENT_SECRET=your_client_secret_here
AAD_TENANT_ID=your_tenant_id_here
```

### Required Permissions
- Add service principal as a user in the Dataverse environment
- Assign appropriate security roles
- API scope: `/.default` for the Dataverse resource

## 🌐 Notes on Endpoints

- Metadata: `$metadata` expects `Accept: application/xml`
- Base: `{DATAVERSE_URL}/api/data/v9.2`
- IDs: GUIDs without braces, e.g., `/accounts(00000000-0000-0000-0000-000000000000)`
- Notes binding: `objectid_<logical>@odata.bind: "/<EntitySet>(<guid>)"`

## 🚨 Error Handling & Resilience

- Retries on timeouts and 5xx with exponential backoff
- Circuit breaker: OPEN → fail fast; HALF_OPEN → trial; CLOSED → normal
- Structured logs include attempt, latency, and status

See `docs/dataverse-troubleshooting.md` for common issues.

## 🔍 Debugging

- `python blc.py dv probe` to verify token, identity, and metadata access
- Enable DEBUG logging for detailed HTTP traces

## 🔄 Async Usage

Dev-layer is sync for terminal ergonomics. For async contexts (e.g., FastAPI), use threads or implement a parallel async client with identical OData semantics.

## 📊 Dependencies

- `httpx` (sync client)
- `azure-identity`
- `structlog` (optional)

---

Last Updated: August 21, 2025
API Version: 1.0.0
