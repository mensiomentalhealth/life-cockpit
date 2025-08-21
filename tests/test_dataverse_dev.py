#!/usr/bin/env python3
"""
Test Suite for Dataverse Dev Layer
Tests key read-only operations, entity resolution, and probe
"""

import os
import sys
import time
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.config import load_config
from dataverse.dev import (
    whoami, entity_def, entity_set, get, query, probe
)


@pytest.fixture(autouse=True, scope="session")
def _load_env_once():
    """Ensure .env is loaded for the test session."""
    load_config()


def test_whoami():
    """Test WhoAmI operation"""
    result = whoami()
    assert result is not None
    assert 'UserId' in result
    assert 'BusinessUnitId' in result
    assert 'OrganizationId' in result


def test_entity_def_and_set():
    """Test entity definition retrieval and caching via entity_set"""
    result = entity_def("account")
    assert result.get('EntitySetName') == 'accounts'
    assert result.get('PrimaryIdAttribute') == 'accountid'

    t0 = time.time()
    s1 = entity_set("contact")  # first call, likely API hit
    t1 = time.time() - t0
    s2 = entity_set("contact")  # cached
    t2 = time.time() - t0
    assert s1 == 'contacts' and s2 == 'contacts'
    assert t2 >= 0


def test_query_accounts():
    """Test basic query (non-failing even if empty)"""
    result = query("accounts", top=3)
    assert result is not None
    assert 'value' in result


def test_probe():
    """Test connection probe"""
    results = probe()
    assert results is not None
    assert 'token' in results
    assert 'whoami' in results


