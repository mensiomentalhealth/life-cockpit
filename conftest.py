#!/usr/bin/env python3
"""
Global pytest configuration
Ensures sandbox is enabled before any test modules import application code.
"""
import os

# Enable sandbox early
os.environ.setdefault("BLC_LOCAL_SANDBOX", "true")
os.environ.setdefault("BLC_REQUIRE_APPROVAL", "false")
os.environ.setdefault("BLC_DRY_RUN_DEFAULT", "true")

try:
    from utils.sandbox import sandbox_manager
    sandbox_manager.enabled = True
    # Also configure guardrails defaults for tests
    from utils.guardrails import guardrail_manager
    guardrail_manager.require_approval = False
    guardrail_manager.dry_run_default = True
except Exception:
    # utils.sandbox may import later; env var is set
    pass


