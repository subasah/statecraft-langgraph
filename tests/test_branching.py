"""Unit tests for Pattern 1: Dynamic Branching & Conditional Routing."""

import pytest
from statecraft.patterns.dynamic_branching import build_branching_graph


def test_branching_security():
    app = build_branching_graph()
    res = app.invoke({"query": "How do I remediate a zero-day authentication bypass vulnerability?"})
    assert res["category"] == "security"
    assert res["selected_route"] == "deep_security_audit"
    assert "deep_security_audit" in res["execution_path"]
    assert "format_response" in res["execution_path"]
    assert "[SECURITY AUDIT ACTIVE]" in res["response"]


def test_branching_technical():
    app = build_branching_graph()
    res = app.invoke({"query": "Our backend microservice is throwing a null pointer crash on startup."})
    assert res["category"] == "technical"
    assert res["selected_route"] == "technical_solver"
    assert "technical_solver" in res["execution_path"]
    assert "[TECHNICAL RESOLUTION]" in res["response"]


def test_branching_billing():
    app = build_branching_graph()
    res = app.invoke({"query": "Requesting a refund for duplicate subscription invoice #1092."})
    assert res["category"] == "billing"
    assert res["selected_route"] == "billing_specialist"
    assert "billing_specialist" in res["execution_path"]
    assert "[BILLING PORTAL]" in res["response"]


def test_branching_general_fast_path():
    app = build_branching_graph()
    res = app.invoke({"query": "What are your office hours on national holidays?"})
    assert res["category"] == "general"
    assert res["selected_route"] == "fast_path_cache"
    assert "fast_path_cache" in res["execution_path"]
    assert "[FAST-PATH CACHE HIT]" in res["response"]
