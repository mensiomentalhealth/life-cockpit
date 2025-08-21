#!/usr/bin/env python3
"""
Pytest configuration for test environment
- Ensures sandbox mode is enabled for tests that expect mock services
"""

import os
import pytest

@pytest.fixture(autouse=True, scope="session")
def _enable_sandbox_mode():
    os.environ["BLC_LOCAL_SANDBOX"] = "true"
    os.environ["BLC_REQUIRE_APPROVAL"] = "false"
    os.environ["BLC_DRY_RUN_DEFAULT"] = "true"
    try:
        # If already imported, force-enable the manager flag
        from utils.sandbox import sandbox_manager
        sandbox_manager.enabled = True
        # Also disable guardrail approvals in tests
        from utils.guardrails import guardrail_manager
        guardrail_manager.require_approval = False
        guardrail_manager.dry_run_default = True
    except Exception:
        pass
    yield

