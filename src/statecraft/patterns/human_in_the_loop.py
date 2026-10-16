"""
Pattern 4: Human-in-the-Loop (HITL) Checkpoints, State Editing & Time-Travel.

High-Level Concept:
Autonomous systems must not act with unchecked agency in high-stakes environments
(e.g., publishing financial filings, executing security patches, or modifying databases).
LangGraph provides native persistence and checkpointing:
1. `interrupt()`: Pauses execution mid-workflow and persists graph state to a checkpointer.
2. The agent yields control to the human reviewer (via web UI, Slack, or CLI).
3. The human inspects the exact state snapshot, and can choose to:
   - APPROVE: Resume execution as-is.
   - EDIT: Mutate variables in state (e.g., refine content or parameters) before resuming.
   - REJECT: Terminate or divert execution down an abort/remediation branch.
4. `Command(resume=...)`: Awakens the paused thread with the human's response.
5. Time-Travel (`get_state_history`): Replay or fork execution from any prior checkpoint.

Architecture:
               [START]
                  │
        [draft_and_score_content]
                  │
        [evaluate_safety_risk]
                  │
        (check_risk_gate)
        ├── if LOW risk ──────────────────────────────────────────┐ (auto-approve)
        └── if ELEVATED / HIGH risk ──> [human_review_checkpoint] ┤
                                              │ (interrupt)        │
                                        <Human Input>              │
                                              │ (Command.resume)   │
                                        (route_decision)           │
                                        ├── if approved / edited ──┴──> [publish_content] ─> [END]
                                        └── if rejected ──────────────> [archive_rejected] ─> [END]
"""

from typing import Dict, Any, List, Literal, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from statecraft.state import HumanInTheLoopState, HumanReviewDecision


def draft_and_score_content(state: HumanInTheLoopState) -> Dict[str, Any]:
    """Node: Drafts the initial content and simulates automated compliance scoring."""
    title = state.get("draft_title", "Quarterly Cloud Infrastructure Modernization")
    body = state.get("draft_body", (
        "Projected migration of core billing microservices to multi-region Kubernetes clusters. "
        "Estimated maintenance downtime: 15 minutes during off-peak weekend hours."
    ))
    risk = state.get("risk_level", "HIGH")
    
    return {
        "draft_title": title,
        "draft_body": body,
        "risk_level": risk,
        "status": "drafting",
        "audit_trail": [f"[Draft Node] Created draft '{title}' with risk rating '{risk}'."]
    }


def evaluate_safety_risk(state: HumanInTheLoopState) -> Dict[str, Any]:
    """Node: Evaluates automated guardrails to determine if human intervention is mandatory."""
    risk = state.get("risk_level", "LOW")
    requires_human = (risk in ["MEDIUM", "HIGH", "CRITICAL"])
    
    notes = []
    if requires_human:
        notes.append(f"Elevated risk tier ({risk}) triggers mandatory human approval policy.")
    else:
        notes.append("Low risk tier passed automated security policies. Eligible for auto-approval.")

    return {
        "human_review_required": requires_human,
        "safety_notes": notes,
        "status": "awaiting_approval" if requires_human else "approved",
        "audit_trail": [f"[Safety Guardrail] Human review required: {requires_human}."]
    }


def check_risk_gate(state: HumanInTheLoopState) -> Literal["human_review_checkpoint", "publish_content"]:
    """Conditional Edge: Routes high-risk content to HITL checkpoint, or low-risk to publish."""
    if state.get("human_review_required", False):
        return "human_review_checkpoint"
    return "publish_content"


def human_review_checkpoint(state: HumanInTheLoopState) -> Dict[str, Any]:
    """HITL Node: Pauses the graph using interrupt() and waits for external reviewer action."""
    # 1. Raise interrupt payload for external inspector
    review_request = {
        "instruction": "Please review this operational draft before production release.",
        "draft_title": state.get("draft_title"),
        "draft_body": state.get("draft_body"),
        "risk_level": state.get("risk_level"),
        "safety_notes": state.get("safety_notes", [])
    }
    
    # Execution halts here until resumed with Command(resume=decision)
    decision: Dict[str, Any] = interrupt(review_request)

    action = decision.get("action", "reject")
    feedback = decision.get("feedback", "No feedback provided")
    edited_content = decision.get("edited_content")
    reviewer = decision.get("reviewed_by", "compliance-officer@enterprise.internal")

    audit_msg = f"[Human Reviewer ({reviewer})] Action: {action.upper()} | Feedback: '{feedback}'"
    updates: Dict[str, Any] = {
        "review_decision": {
            "action": action,
            "feedback": feedback,
            "edited_content": edited_content,
            "reviewed_by": reviewer
        },
        "audit_trail": [audit_msg]
    }

    if action == "edit" and edited_content:
        updates["draft_body"] = edited_content
        updates["status"] = "approved"
        updates["audit_trail"] = [audit_msg, "[State Mutation] Draft content updated with human edits."]
    elif action == "approve":
        updates["status"] = "approved"
    else:
        updates["status"] = "rejected"

    return updates


def route_decision(state: HumanInTheLoopState) -> Literal["publish_content", "archive_rejected"]:
    """Conditional Edge: Directs workflow based on human reviewer's verdict."""
    decision = state.get("review_decision")
    if not decision:
        return "archive_rejected"
    
    action = decision.get("action", "reject")
    if action in ["approve", "edit"]:
        return "publish_content"
    return "archive_rejected"


def publish_content(state: HumanInTheLoopState) -> Dict[str, Any]:
    """Node: Final publication and broadcast after safety approval."""
    title = state.get("draft_title", "")
    body = state.get("draft_body", "")
    published_msg = f"=== OFFICIAL BROADCAST ===\nTITLE: {title}\nBODY: {body}\nSTATUS: VERIFIED & PUBLISHED"
    return {
        "published_output": published_msg,
        "status": "published",
        "audit_trail": ["[Publish] Content securely published to enterprise channel."]
    }


def archive_rejected(state: HumanInTheLoopState) -> Dict[str, Any]:
    """Node: Clean archival and notification on rejected draft."""
    feedback = state.get("review_decision", {}).get("feedback", "Policy non-compliance")
    return {
        "published_output": None,
        "status": "rejected",
        "audit_trail": [f"[Archived] Draft rejected by human reviewer. Reason: {feedback}"]
    }


def build_hitl_graph(checkpointer: Optional[Any] = None):
    """Compiles and returns the Human-in-the-Loop StateGraph with checkpointing."""
    if checkpointer is None:
        checkpointer = MemorySaver()

    graph = StateGraph(HumanInTheLoopState)

    # 1. Add nodes
    graph.add_node("draft_and_score_content", draft_and_score_content)
    graph.add_node("evaluate_safety_risk", evaluate_safety_risk)
    graph.add_node("human_review_checkpoint", human_review_checkpoint)
    graph.add_node("publish_content", publish_content)
    graph.add_node("archive_rejected", archive_rejected)

    # 2. Add edges
    graph.add_edge(START, "draft_and_score_content")
    graph.add_edge("draft_and_score_content", "evaluate_safety_risk")

    # 3. Conditional routing to checkpoint
    graph.add_conditional_edges(
        "evaluate_safety_risk",
        check_risk_gate,
        {
            "human_review_checkpoint": "human_review_checkpoint",
            "publish_content": "publish_content"
        }
    )

    # 4. Conditional routing after human review
    graph.add_conditional_edges(
        "human_review_checkpoint",
        route_decision,
        {
            "publish_content": "publish_content",
            "archive_rejected": "archive_rejected"
        }
    )

    graph.add_edge("publish_content", END)
    graph.add_edge("archive_rejected", END)

    return graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    checkpointer = MemorySaver()
    app = build_hitl_graph(checkpointer=checkpointer)
    thread_config = {"configurable": {"thread_id": "compliance-review-9901"}}

    print("="*60)
    print("STEP 1: Starting High-Risk Workflow (Expect Interrupt at Checkpoint)...")
    res1 = app.invoke({
        "draft_title": "Production DB Schema Migration v2.4",
        "draft_body": "DROP COLUMN legacy_user_hash; ADD COLUMN secure_uuid_v7 VARCHAR(36);",
        "risk_level": "CRITICAL",
        "audit_trail": []
    }, config=thread_config)

    # Inspect paused state
    current_state = app.get_state(thread_config)
    print(f"\nExecution Paused! Next Node(s) to run: {current_state.next}")
    if current_state.tasks and current_state.tasks[0].interrupts:
        interrupt_val = current_state.tasks[0].interrupts[0].value
        print(f"Interrupt Request Payload:\n  {interrupt_val}")

    print("\n" + "="*60)
    print("STEP 2: Human Reviewer Provides Edit + Approval via Command(resume=...)...")
    resume_command = Command(resume={
        "action": "edit",
        "feedback": "Approved with safety precaution: keep legacy column as deprecated for 30 days.",
        "edited_content": "ALTER TABLE users ADD COLUMN secure_uuid_v7 VARCHAR(36); -- legacy_user_hash marked deprecated",
        "reviewed_by": "alice.principal.architect@corp.internal"
    })
    
    res2 = app.invoke(resume_command, config=thread_config)
    print(f"\nResumed! Final Status: {res2['status']}")
    print("\nAudit Trail:")
    for entry in res2["audit_trail"]:
        print(f"  {entry}")
    print("\nFinal Published Output:\n" + str(res2["published_output"]))
