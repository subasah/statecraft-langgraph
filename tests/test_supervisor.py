"""Unit tests for Pattern 5: Hierarchical Supervisor & Multi-Agent Subgraph."""

import pytest
from statecraft.patterns.hierarchical_supervisor import build_supervisor_graph


def test_supervisor_orchestrates_all_specialists():
    app = build_supervisor_graph()
    initial_state = {
        "objective": "Zero-Trust API Gateway Token Deserialization Security Hardening",
        "worker_outputs": {},
        "completed_subtasks": [],
        "supervisor_notes": [],
        "iterations": 0,
        "max_iterations": 10
    }
    result = app.invoke(initial_state)

    assert "researcher" in result["worker_outputs"]
    assert "engineer" in result["worker_outputs"]
    assert "auditor" in result["worker_outputs"]
    assert len(result["completed_subtasks"]) == 3
    assert result["final_synthesis"] is not None
    assert "EXECUTIVE MULTI-AGENT SYNTHESIS BRIEFING" in result["final_synthesis"]
    assert "CERTIFIED FOR PRODUCTION LAUNCH" in result["final_synthesis"]
