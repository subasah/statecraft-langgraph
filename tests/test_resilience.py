"""Unit tests for Pattern 3: Resilience, Retries & Fallback Circuit."""

import pytest
from statecraft.patterns.resilience_retries import build_resilience_graph


def test_resilience_flaky_service_recovers():
    app = build_resilience_graph()
    res = app.invoke({
        "endpoint": "https://api.internal/flaky_telemetry",
        "max_retries": 3,
        "attempt": 0,
        "failures_encountered": [],
        "execution_trace": []
    })

    assert res["fallback_used"] is False
    assert res["circuit_state"] == "CLOSED"
    assert res["attempt"] == 3
    assert len(res["failures_encountered"]) == 2
    assert res["data"] is not None
    assert res["data"]["status"] == "healthy"


def test_resilience_down_service_trips_circuit_breaker():
    app = build_resilience_graph()
    res = app.invoke({
        "endpoint": "https://api.internal/down_service",
        "max_retries": 3,
        "attempt": 0,
        "failures_encountered": [],
        "execution_trace": []
    })

    assert res["fallback_used"] is True
    assert res["circuit_state"] == "OPEN"
    assert res["attempt"] == 3
    assert len(res["failures_encountered"]) == 3
    assert res["data"]["source"] == "L2_REDIS_FALLBACK_CACHE"
