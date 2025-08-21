#!/usr/bin/env python3
"""
Dataverse HTTP Client
Simple httpx client with proper headers and impersonation
"""
import os
import httpx
from typing import Dict, Optional
from .auth import dv_token

def get_base_url() -> str:
    """Get the Dataverse base URL"""
    return f"{os.environ['DATAVERSE_URL'].rstrip('/')}/api/data/v9.2"

def dv_client(impersonate_user_id: str | None = None) -> httpx.Client:
    """Create httpx client with Dataverse headers"""
    headers = {
        "Authorization": f"Bearer {dv_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Prefer": 'return=representation,odata.include-annotations="*"',
    }
    if impersonate_user_id:
        headers["MSCRMCallerID"] = impersonate_user_id
    return httpx.Client(
        base_url=get_base_url(),
        headers=headers,
        timeout=httpx.Timeout(15.0, connect=5.0),
        http2=True,
        limits=httpx.Limits(
            max_keepalive_connections=5,
            max_connections=10,
            keepalive_expiry=30,
        ),
    )

# Simple connection pool: cache clients by impersonation id (None for default)
_pooled_clients: Dict[Optional[str], httpx.Client] = {}

def get_pooled_client(impersonate_user_id: Optional[str] = None) -> httpx.Client:
    """Return a pooled httpx.Client for reuse across requests."""
    global _pooled_clients
    key = impersonate_user_id
    client = _pooled_clients.get(key)
    if client is None or client.is_closed:
        _pooled_clients[key] = dv_client(impersonate_user_id)
    return _pooled_clients[key]

def close_pooled_clients() -> None:
    """Close all pooled clients (for shutdown/cleanup)."""
    global _pooled_clients
    for client in _pooled_clients.values():
        try:
            if not client.is_closed:
                client.close()
        except Exception:
            pass
    _pooled_clients.clear()
