#!/usr/bin/env python3
"""
Dataverse Authentication
Simple azure-identity based token acquisition
"""
import os
from azure.identity import ClientSecretCredential

def dv_token() -> str:
    """Get Dataverse access token"""
    # Prefer AAD_*; fall back to AZURE_* for local compatibility
    tenant_id = os.getenv("AAD_TENANT_ID") or os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AAD_CLIENT_ID") or os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AAD_CLIENT_SECRET") or os.getenv("AZURE_CLIENT_SECRET")
    if not (tenant_id and client_id and client_secret):
        missing = [k for k, v in {
            "AAD_TENANT_ID": os.getenv("AAD_TENANT_ID"),
            "AAD_CLIENT_ID": os.getenv("AAD_CLIENT_ID"),
            "AAD_CLIENT_SECRET": os.getenv("AAD_CLIENT_SECRET"),
            "AZURE_TENANT_ID": os.getenv("AZURE_TENANT_ID"),
            "AZURE_CLIENT_ID": os.getenv("AZURE_CLIENT_ID"),
            "AZURE_CLIENT_SECRET": os.getenv("AZURE_CLIENT_SECRET"),
        }.items() if v is None]
        raise KeyError(f"Missing required AAD/AZURE env vars for Dataverse auth: {', '.join(missing)}")

    cred = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )
    resource = os.environ["DATAVERSE_URL"].rstrip("/")
    return cred.get_token(f"{resource}/.default").token
