#!/usr/bin/env python3
import os

from utils.config import load_config


def test_normalizes_aad_to_azure(monkeypatch):
    monkeypatch.setenv("BLC_SKIP_DOTENV", "true")
    monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("AZURE_TENANT_ID", raising=False)

    monkeypatch.setenv("AAD_CLIENT_ID", "cid")
    monkeypatch.setenv("AAD_CLIENT_SECRET", "sec")
    monkeypatch.setenv("AAD_TENANT_ID", "tid")
    monkeypatch.setenv("DATAVERSE_URL", "https://example.crm.dynamics.com")

    load_config()

    assert os.getenv("AZURE_CLIENT_ID") == "cid"
    assert os.getenv("AZURE_CLIENT_SECRET") == "sec"
    assert os.getenv("AZURE_TENANT_ID") == "tid"


def test_keeps_existing_azure_if_present(monkeypatch):
    monkeypatch.setenv("BLC_SKIP_DOTENV", "true")
    monkeypatch.setenv("AAD_CLIENT_ID", "cid_aad")
    monkeypatch.setenv("AZURE_CLIENT_ID", "cid_azure")
    monkeypatch.setenv("AAD_CLIENT_SECRET", "sec_aad")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "sec_azure")
    monkeypatch.setenv("AAD_TENANT_ID", "tid_aad")
    monkeypatch.setenv("AZURE_TENANT_ID", "tid_azure")
    monkeypatch.setenv("DATAVERSE_URL", "https://example.crm.dynamics.com")

    load_config()

    assert os.getenv("AZURE_CLIENT_ID") == "cid_azure"
    assert os.getenv("AZURE_CLIENT_SECRET") == "sec_azure"
    assert os.getenv("AZURE_TENANT_ID") == "tid_azure"


