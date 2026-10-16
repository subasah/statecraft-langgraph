"""Unit tests for Pattern 4: Human-in-the-Loop Checkpoints & Time Travel."""

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from statecraft.patterns.human_in_the_loop import build_hitl_graph


def test_hitl_low_risk_auto_approves():
    checkpointer = MemorySaver()
    app = build_hitl_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "auto-approve-thread"}}

    res = app.invoke({
        "draft_title": "Routine Cache TTL Update",
        "draft_body": "Update redis TTL from 60s to 120s for catalog queries.",
        "risk_level": "LOW",
        "audit_trail": []
    }, config=config)

    assert res["status"] == "published"
    assert res["human_review_required"] is False
    assert res["published_output"] is not None


def test_hitl_high_risk_pauses_and_resumes_with_approval():
    checkpointer = MemorySaver()
    app = build_hitl_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "approval-thread-42"}}

    # Step 1: Pauses at checkpoint
    app.invoke({
        "draft_title": "Production Secret Key Rotation",
        "draft_body": "Rotate RSA-4096 signing key in IAM key vault.",
        "risk_level": "HIGH",
        "audit_trail": []
    }, config=config)

    state = app.get_state(config)
    assert "human_review_checkpoint" in state.next
    assert len(state.tasks[0].interrupts) > 0

    # Step 2: Resume with approval
    resumed = app.invoke(Command(resume={
        "action": "approve",
        "feedback": "Key rotation verified by Security Lead.",
        "reviewed_by": "secops-lead@enterprise.internal"
    }), config=config)

    assert resumed["status"] == "published"
    assert resumed["review_decision"]["action"] == "approve"
    assert "VERIFIED & PUBLISHED" in resumed["published_output"]


def test_hitl_resumes_with_human_edits_mutating_state():
    checkpointer = MemorySaver()
    app = build_hitl_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "edit-thread-88"}}

    app.invoke({
        "draft_title": "Database Schema Index Update",
        "draft_body": "CREATE INDEX idx_user_email ON users(email);",
        "risk_level": "CRITICAL",
        "audit_trail": []
    }, config=config)

    # Human edits content to include CONCURRENTLY for safety
    resumed = app.invoke(Command(resume={
        "action": "edit",
        "feedback": "Added CONCURRENTLY keyword to prevent locking production tables.",
        "edited_content": "CREATE INDEX CONCURRENTLY idx_user_email ON users(email);",
        "reviewed_by": "lead.dba@enterprise.internal"
    }), config=config)

    assert resumed["status"] == "published"
    assert "CONCURRENTLY" in resumed["draft_body"]
    assert "CONCURRENTLY" in resumed["published_output"]
