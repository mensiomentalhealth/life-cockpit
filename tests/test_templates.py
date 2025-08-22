#!/usr/bin/env python3
"""
Tests for the Template System (utils/templates.py)
"""
import os
import json

from utils.templates import discover_templates, load_template_by_name, render_template


def test_discover_templates_basic():
    templates = discover_templates()
    assert isinstance(templates, list)
    # At least the example template is present
    names = [t.meta.name for t in templates]
    assert "session-summary" in names


def test_load_and_render_session_summary(tmp_path):
    tmpl = load_template_by_name("session-summary")
    context = {
        "client_name": "Test Client",
        "session_date": "2025-08-21",
        "summary_text": "Did CBT exercises; planned follow-up.",
    }
    output = render_template(tmpl, context)
    assert "Session Summary for Test Client" in output
    assert "2025-08-21" in output
    assert "Did CBT exercises" in output


def test_missing_required_vars_raises():
    tmpl = load_template_by_name("session-summary")
    context = {
        # missing client_name
        "session_date": "2025-08-21",
        "summary_text": "...",
    }
    try:
        render_template(tmpl, context)
        assert False, "Expected ValueError for missing required vars"
    except ValueError as e:
        assert "Missing required template variables" in str(e)


