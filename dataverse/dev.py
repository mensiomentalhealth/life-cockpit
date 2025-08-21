#!/usr/bin/env python3
"""
Dataverse Dev Layer
Basic CRUD operations for Dataverse with proper OData handling
"""
import time
import httpx
from typing import Callable, Any
import structlog
from .client import dv_client, get_pooled_client
from .circuit_breaker import dataverse_breaker

_entity_cache: dict[str, str] = {}  # logical -> EntitySetName
_logger = structlog.get_logger(__name__)

def _with_retry(fn: Callable[[], Any], max_retries: int = 3, backoff_factor: float = 2.0) -> Any:
    """Execute callable with exponential backoff retry for transient errors."""
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            start = time.time()
            result = fn()
            duration = time.time() - start
            _logger.info("dv_call_success", attempt=attempt + 1, duration_ms=int(duration * 1000))
            return result
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            last_exc = exc
            _logger.warning("dv_call_transient_error", attempt=attempt + 1, error=str(exc))
        except httpx.HTTPStatusError as exc:
            # Retry only on 5xx
            if exc.response is not None and 500 <= exc.response.status_code < 600:
                last_exc = exc
                _logger.warning("dv_call_5xx", attempt=attempt + 1, status_code=exc.response.status_code)
            else:
                _logger.error("dv_call_http_error", status_code=exc.response.status_code if exc.response else None)
                raise
        if attempt < max_retries - 1:
            wait_s = backoff_factor ** attempt
            _logger.info("dv_call_retry", next_backoff_s=wait_s)
            time.sleep(wait_s)
    assert last_exc is not None
    _logger.error("dv_call_failed", error=str(last_exc))
    raise last_exc

@dataverse_breaker
def whoami(impersonate: str | None = None) -> dict:
    """Get current user info"""
    def _op():
        c = get_pooled_client(impersonate)
        r = c.get("/WhoAmI")
        r.raise_for_status()
        return r.json()
    return _with_retry(_op)

@dataverse_breaker
def entity_def(logical_name: str) -> dict:
    """Get entity definition for logical name"""
    def _op():
        c = get_pooled_client()
        r = c.get(
            f"/EntityDefinitions(LogicalName='{logical_name}')",
            params={"$select": "EntitySetName,PrimaryIdAttribute,PrimaryNameAttribute"},
        )
        r.raise_for_status()
        return r.json()
    return _with_retry(_op)

def entity_set(logical_name: str) -> str:
    """Get EntitySetName for logical name (cached)"""
    if logical_name not in _entity_cache:
        _entity_cache[logical_name] = entity_def(logical_name)["EntitySetName"]
    return _entity_cache[logical_name]

@dataverse_breaker
def get(entity_set_name: str, id: str, select: str | None = None, expand: str | None = None) -> dict:
    """Get single record by ID"""
    params = {}
    if select:
        params["$select"] = select
    if expand:
        params["$expand"] = expand
    def _op():
        c = get_pooled_client()
        r = c.get(f"/{entity_set_name}({id})", params=params)
        r.raise_for_status()
        return r.json()
    return _with_retry(_op)

@dataverse_breaker
def query(entity_set_name: str, filter: str = "", select: str = "", top: int = 10) -> dict:
    """Query records with OData parameters"""
    params = {"$top": top, "$count": "true"}  # ✅ $count=true included
    if filter:
        params["$filter"] = filter
    if select:
        params["$select"] = select
    def _op():
        c = get_pooled_client()
        r = c.get(f"/{entity_set_name}", params=params)
        r.raise_for_status()
        return r.json()  # ✅ @odata.count will be in the response
    return _with_retry(_op)

@dataverse_breaker
def create(entity_set_name: str, payload: dict, *, impersonate: str | None = None) -> dict:
    """Create new record"""
    def _op():
        c = get_pooled_client(impersonate)
        r = c.post(f"/{entity_set_name}", json=payload)
        r.raise_for_status()
        oid = r.headers.get("OData-EntityId", "")
        if oid.endswith(")"):
            gid = oid[oid.rfind("(") + 1:-1]
            return {"id": gid}
        return {"id": "unknown"}
    return _with_retry(_op)

@dataverse_breaker
def update(entity_set_name: str, id: str, payload: dict, *, impersonate: str | None = None) -> None:
    """Update existing record"""
    def _op():
        c = get_pooled_client(impersonate)
        r = c.patch(f"/{entity_set_name}({id})", json=payload)
        r.raise_for_status()
    return _with_retry(_op)

@dataverse_breaker
def delete(entity_set_name: str, id: str, *, impersonate: str | None = None) -> None:
    """Delete record"""
    def _op():
        c = get_pooled_client(impersonate)
        r = c.delete(f"/{entity_set_name}({id})")
        r.raise_for_status()
    return _with_retry(_op)

@dataverse_breaker
def create_note(regarding_logical: str, regarding_id: str, subject: str, notetext: str, *,
                impersonate: str | None = None) -> dict:
    """Create note attached to record"""
    set_name = entity_set(regarding_logical)
    payload = {
        "subject": subject,
        "notetext": notetext,
        f"objectid_{regarding_logical}@odata.bind": f"/{set_name}({regarding_id})",  # ✅ Correct binding
    }
    def _op():
        c = get_pooled_client(impersonate)
        r = c.post("/annotations", json=payload)
        r.raise_for_status()
        oid = r.headers.get("OData-EntityId", "")
        if oid.endswith(")"):
            gid = oid[oid.rfind("(") + 1:-1]
            return {"id": gid}
        return {"id": "unknown"}
    return _with_retry(_op)

def find_user_systemuserid(upn_or_domainname: str) -> str:
    """Find systemuserid by domain name or UPN"""
    data = query("systemusers",
                 filter=f"(userprincipalname eq '{upn_or_domainname}' or domainname eq '{upn_or_domainname}')",
                 select="systemuserid", top=1)
    vals = data.get("value", [])
    if not vals:
        raise RuntimeError(f"user not found: {upn_or_domainname}")
    return vals[0]["systemuserid"]

def probe() -> dict:
    """Smoke test the Dataverse connection"""
    results = {}
    
    # Test token
    try:
        from .auth import dv_token
        token = dv_token()
        results["token"] = "✅ Valid token acquired"
    except Exception as e:
        results["token"] = f"❌ Token error: {e}"
        return results
    
    # Test WhoAmI
    try:
        whoami_result = whoami()
        results["whoami"] = f"✅ App user: {whoami_result.get('UserId')}"
    except Exception as e:
        results["whoami"] = f"❌ WhoAmI error: {e}"
    
    # Test metadata
    try:
        with dv_client() as c:
            headers = {"Accept": "application/xml"}
            # Use a higher per-request timeout for metadata, which can be large
            metadata_timeout = httpx.Timeout(60.0, connect=10.0, read=60.0)
            r = c.get("/$metadata", headers=headers, timeout=metadata_timeout)
            r.raise_for_status()
            results["metadata"] = "✅ Metadata accessible"
    except Exception as e:
        results["metadata"] = f"❌ Metadata error: {e}"
    
    return results
