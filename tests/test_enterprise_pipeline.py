"""Integration tests for Flagship Enterprise Orchestrator Pipeline."""

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from statecraft.orchestrator.enterprise_pipeline import build_enterprise_pipeline


def test_enterprise_pipeline_standard_track():
    checkpointer = MemorySaver()
    app = build_enterprise_pipeline(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "std-pipeline-01"}}

    # Low-risk standard ticket: Auto-deploys without human pause
    initial_state = {
        "ticket_id": "TICKET-STD-10",
        "requirement": "Format and calculate moving average statistics for UI dashboard.",
        "max_correction_cycles": 3,
        "correction_cycles": 0,
        "pipeline_trace": []
    }
    app.invoke(initial_state, config=config)
    state = app.get_state(config)

    assert state.values["risk_tier"] == "TIER_1_STANDARD"
    assert state.values["branch_taken"] == "STANDARD_AUTOMATED_TRACK"
    assert state.values["deployment_status"] == "DEPLOYED"
    assert "PRODUCTION RELEASE MANIFEST" in state.values["release_notes"]


def test_enterprise_pipeline_critical_track_with_hitl_signoff():
    checkpointer = MemorySaver()
    app = build_enterprise_pipeline(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "crit-pipeline-99"}}

    # High-risk security ticket: Pauses for HITL governance signoff
    initial_state = {
        "ticket_id": "TICKET-CRIT-99",
        "requirement": "Zero-trust security auth token moving average calculation with crypto boundary checks.",
        "max_correction_cycles": 3,
        "correction_cycles": 0,
        "pipeline_trace": []
    }
    app.invoke(initial_state, config=config)
    paused_state = app.get_state(config)

    assert paused_state.values["risk_tier"] == "TIER_3_CRITICAL"
    assert "human_governance_checkpoint" in paused_state.next
    assert len(paused_state.tasks[0].interrupts) > 0

    # Resume with approval
    resumed = app.invoke(Command(resume={
        "action": "approve",
        "feedback": "SecOps approval granted after cryptographic verification.",
        "reviewed_by": "vp.infosec@enterprise.internal"
    }), config=config)

    assert resumed["deployment_status"] == "DEPLOYED"
    assert "Security Sign-off: VERIFIED" in resumed["release_notes"]
