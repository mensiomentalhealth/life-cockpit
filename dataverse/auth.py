#!/usr/bin/env python3
"""
Dataverse Authentication
Simple azure-identity based token acquisition
"""
import os
from azure.identity import ClientSecretCredential

def dv_token() -> str:
    """Get Dataverse access token"""
    cred = ClientSecretCredential(
        tenant_id=os.environ["AAD_TENANT_ID"],
        client_id=os.environ["AAD_CLIENT_ID"],
        client_secret=os.environ["AAD_CLIENT_SECRET"],
    )
    resource = os.environ["DATAVERSE_URL"].rstrip("/")
    return cred.get_token(f"{resource}/.default").token
