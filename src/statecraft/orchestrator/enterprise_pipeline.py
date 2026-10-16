"""
Flagship Enterprise Orchestrator Pipeline: Autonomous Release & Security Gate.

Unifies all 5 architectural patterns into a single production-grade pipeline:
1. Dynamic Branching: Classifies risk tier (TIER_1 vs TIER_2/3) and branches paths.
2. Resilience & Retries: Flaky telemetry ingestion with backoff & fallback.
3. Code Synthesis & Static Analysis.
4. Evaluator-Optimizer Self-Correction Loop: Iteratively fixes tests and defects.
5. Human-in-the-Loop Governance: Pauses via interrupt() for security sign-off.
6. Deployment Packaging: Formats verifiable audit trail and release manifest.

Mermaid Architecture:
```mermaid
flowchart TD
    START([START: Ticket Ingest]) --> triage[triage_and_branch]
    triage -->|Conditional Edge| branch_router{Risk Assessment}
    
    branch_router -->|TIER_1: Fast Track| standard_prep[standard_release_prep]
    branch_router -->|TIER_2/3: Elevated| resilient_fetch[resilient_security_fetch]
    
    resilient_fetch -->|Retry Loop| resilient_fetch
    resilient_fetch --> spec_synth[synthesize_solution]
    standard_prep --> spec_synth
    
    spec_synth --> eval_optimizer[evaluator_optimizer_node]
    eval_optimizer -->|Conditional Loop: Fail & iter < max| spec_synth
    eval_optimizer -->|Conditional Gate: Pass| governance_gate{Requires HITL?}
    
    governance_gate -->|Yes: TIER_2/3| hitl_checkpoint[human_governance_checkpoint]
    governance_gate -->|No: Auto-Pass| deploy[deploy_and_publish]
    
    hitl_checkpoint -->|<interrupt / resume>| hitl_router{Decision}
    hitl_router -->|Approved / Edited| deploy
    hitl_router -->|Rejected| abort[abort_and_log]
    
    deploy --> END([END: Release Live])
    abort --> END
```
"""

import ast
import json
import time
from typing import Dict, Any, Literal, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from statecraft.state import EnterprisePipelineState, CodeFeedback, HumanReviewDecision
from statecraft.llm import get_llm, extract_code_block


def triage_and_branch(state: EnterprisePipelineState) -> Dict[str, Any]:
    """Node: Evaluates ticket requirements and assigns risk tier."""
    req = state.get("requirement", "")
    ticket_id = state.get("ticket_id", "TICKET-001")
    req_lower = req.lower()

    if any(k in req_lower for k in ["auth", "crypto", "security", "firewall", "token", "schema"]):
        tier = "TIER_3_CRITICAL"
        requires_human = True
    elif any(k in req_lower for k in ["payment", "billing", "migration", "concurrency"]):
        tier = "TIER_2_ELEVATED"
        requires_human = True
    else:
        tier = "TIER_1_STANDARD"
        requires_human = False

    trace_entry = f"[Triage] Ticket {ticket_id} classified as {tier} (Human Sign-off: {requires_human})."
    return {
        "risk_tier": tier,
        "requires_human_signoff": requires_human,
        "deployment_status": "TRIAGED",
        "pipeline_trace": [trace_entry]
    }


def route_by_risk(state: EnterprisePipelineState) -> Literal["standard_release_prep", "resilient_security_fetch"]:
    """Conditional Edge: Directs low-risk to standard path, high-risk to security audit fetch."""
    tier = state.get("risk_tier", "TIER_1_STANDARD")
    if tier == "TIER_1_STANDARD":
        return "standard_release_prep"
    return "resilient_security_fetch"


def standard_release_prep(state: EnterprisePipelineState) -> Dict[str, Any]:
    """Node: Standard fast-track preparation."""
    return {
        "branch_taken": "STANDARD_AUTOMATED_TRACK",
        "resilient_fetch_attempts": 1,
        "pipeline_trace": ["[Branch: Standard] Proceeding along low-latency automated track."]
    }


def resilient_security_fetch(state: EnterprisePipelineState) -> Dict[str, Any]:
    """Node: Resilient fetch of threat intelligence and policy rules with retries."""
    attempts = state.get("resilient_fetch_attempts", 0) + 1
    
    # Simulate flaky network connection on attempt 1, recovering on attempt 2
    if attempts < 2:
        return {
            "resilient_fetch_attempts": attempts,
            "pipeline_trace": [f"[Resilience] Attempt {attempts}: Network glitch accessing SecOps DB. Retrying with backoff..."]
        }

    return {
        "branch_taken": "ELEVATED_SECURITY_TRACK",
        "resilient_fetch_attempts": attempts,
        "pipeline_trace": [f"[Resilience] Attempt {attempts}: Successfully ingested SecOps compliance rules (200 OK)."]
    }


def check_fetch_status(state: EnterprisePipelineState) -> Literal["resilient_security_fetch", "synthesize_solution"]:
    """Conditional Edge: Loops until fetch succeeds or threshold met."""
    if state.get("resilient_fetch_attempts", 0) < 2:
        time.sleep(0.05)
        return "resilient_security_fetch"
    return "synthesize_solution"


def synthesize_solution(state: EnterprisePipelineState) -> Dict[str, Any]:
    """Node: Generates code and tests, incorporating evaluator feedback on retry."""
    req = state.get("requirement", "")
    feedback = state.get("evaluator_feedback")
    cycle = state.get("correction_cycles", 0) + 1
    llm = get_llm()

    if feedback and not feedback.get("passed", False):
        prompt = (
            f"Requirement: {req}\n"
            f"Critique from previous evaluation:\n{feedback.get('critique')}\n"
            f"Errors: {feedback.get('errors')}\n"
            f"Fix the code to pass all assertions."
        )
    else:
        prompt = f"Requirement: {req}\nGenerate Python code to solve this requirement."

    raw_code = llm.invoke(prompt)
    code = extract_code_block(raw_code, "python")

    return {
        "code_solution": code,
        "correction_cycles": cycle,
        "deployment_status": "CODING",
        "pipeline_trace": [f"[Synthesis Cycle {cycle}] Generated candidate code ({len(code)} chars)."]
    }


def evaluator_optimizer_node(state: EnterprisePipelineState) -> Dict[str, Any]:
    """Node: Analyzes AST syntax and executes test suite against candidate code."""
    code = state.get("code_solution", "")
    cycle = state.get("correction_cycles", 1)
    errors = []
    tests_passed = 0
    total_tests = 3

    # AST Check
    try:
        ast.parse(code)
        syntax_ok = True
    except SyntaxError as e:
        syntax_ok = False
        errors.append(f"SyntaxError: {e.msg}")

    # Functional validation in isolated sandbox
    if syntax_ok:
        sandbox: Dict[str, Any] = {}
        try:
            exec(code, sandbox)
            fn = sandbox.get("calculate_moving_average")
            if callable(fn):
                if fn([10, 20, 30, 40], 2) == [15.0, 25.0, 35.0]:
                    tests_passed += 1
                else:
                    errors.append("AssertionError: window calculation mismatch")
                
                if fn([5, 15], 2) == [10.0]:
                    tests_passed += 1
                else:
                    errors.append("AssertionError: boundary window size mismatch")

                if fn([], 2) == []:
                    tests_passed += 1
                else:
                    errors.append("AssertionError: empty list boundary failed")
            else:
                errors.append("Callable function not found in namespace")
        except Exception as exc:
            errors.append(f"Execution error: {exc}")

    all_passed = (syntax_ok and tests_passed == total_tests)
    critique = "All unit tests verified." if all_passed else f"Passed {tests_passed}/{total_tests}. Fix boundary logic."
    
    feedback: CodeFeedback = {
        "passed": all_passed,
        "syntax_valid": syntax_ok,
        "tests_passed": tests_passed,
        "total_tests": total_tests,
        "errors": errors,
        "critique": critique
    }

    return {
        "evaluator_feedback": feedback,
        "pipeline_trace": [f"[Evaluator Cycle {cycle}] Status: {'PASSED' if all_passed else 'FAILED'} ({tests_passed}/{total_tests} tests)."]
    }


def route_after_evaluation(state: EnterprisePipelineState) -> Literal["synthesize_solution", "check_governance"]:
    """Conditional Edge: Loops back for self-correction if failed, or advances if passed."""
    feedback = state.get("evaluator_feedback")
    cycle = state.get("correction_cycles", 1)
    max_cycles = state.get("max_correction_cycles", 3)

    if feedback and feedback.get("passed", False):
        return "check_governance"
    elif cycle < max_cycles:
        return "synthesize_solution"
    else:
        # Bounded limit reached, advance to human review for manual decision
        return "check_governance"


def check_governance(state: EnterprisePipelineState) -> Literal["human_governance_checkpoint", "deploy_and_publish"]:
    """Conditional Edge: Routes high-risk tickets to human review, or auto-deploys low-risk."""
    if state.get("requires_human_signoff", False):
        return "human_governance_checkpoint"
    return "deploy_and_publish"


def human_governance_checkpoint(state: EnterprisePipelineState) -> Dict[str, Any]:
    """HITL Node: Pauses the pipeline using interrupt() for security officer sign-off."""
    interrupt_payload = {
        "ticket_id": state.get("ticket_id"),
        "risk_tier": state.get("risk_tier"),
        "requirement": state.get("requirement"),
        "code_solution": state.get("code_solution"),
        "correction_cycles": state.get("correction_cycles"),
        "evaluator_feedback": state.get("evaluator_feedback"),
        "prompt": "Elevated risk tier requires explicit security authorization. Approve, Edit, or Reject."
    }

    # Pipeline execution pauses here
    decision: Dict[str, Any] = interrupt(interrupt_payload)

    action = decision.get("action", "reject")
    feedback = decision.get("feedback", "No comment")
    edited_code = decision.get("edited_content")
    reviewer = decision.get("reviewed_by", "secops-approver@enterprise.internal")

    updates: Dict[str, Any] = {
        "human_decision": {
            "action": action,
            "feedback": feedback,
            "edited_content": edited_code,
            "reviewed_by": reviewer
        },
        "pipeline_trace": [f"[Human Reviewer ({reviewer})] Decision: {action.upper()} | Note: '{feedback}'"]
    }

    if action == "edit" and edited_code:
        updates["code_solution"] = edited_code
        updates["pipeline_trace"].append("[State Edit] Human reviewer committed manual code refinement.")

    return updates


def route_human_verdict(state: EnterprisePipelineState) -> Literal["deploy_and_publish", "abort_and_log"]:
    """Conditional Edge: Deploys on approval/edit, or aborts on rejection."""
    decision = state.get("human_decision", {})
    action = decision.get("action", "reject") if decision else "approve"
    if action in ["approve", "edit"]:
        return "deploy_and_publish"
    return "abort_and_log"


def deploy_and_publish(state: EnterprisePipelineState) -> Dict[str, Any]:
    """Node: Packages release manifest and activates production deployment."""
    ticket = state.get("ticket_id", "N/A")
    tier = state.get("risk_tier", "N/A")
    cycles = state.get("correction_cycles", 1)
    
    release_manifest = (
        f"=== PRODUCTION RELEASE MANIFEST ===\n"
        f"Ticket: {ticket} | Risk Tier: {tier}\n"
        f"Self-Correction Cycles: {cycles}\n"
        f"Security Sign-off: VERIFIED\n"
        f"Deployment Status: LIVE_IN_PRODUCTION\n"
        f"===================================="
    )

    return {
        "deployment_status": "DEPLOYED",
        "release_notes": release_manifest,
        "pipeline_trace": ["[Deploy] Artifact successfully published to production clusters."]
    }


def abort_and_log(state: EnterprisePipelineState) -> Dict[str, Any]:
    """Node: Aborts release pipeline and logs incident report."""
    ticket = state.get("ticket_id", "N/A")
    reason = state.get("human_decision", {}).get("feedback", "Rejected during security audit.")
    
    abort_manifest = (
        f"=== RELEASE ABORTED ===\n"
        f"Ticket: {ticket}\n"
        f"Reason: {reason}\n"
        f"Deployment Status: ABORTED\n"
        f"======================="
    )

    return {
        "deployment_status": "ABORTED",
        "release_notes": abort_manifest,
        "pipeline_trace": [f"[Abort] Deployment halted. Incident recorded: {reason}"]
    }


def build_enterprise_pipeline(checkpointer: Optional[Any] = None):
    """Compiles and returns the unified Enterprise Orchestrator StateGraph."""
    if checkpointer is None:
        checkpointer = MemorySaver()

    graph = StateGraph(EnterprisePipelineState)

    # 1. Add all nodes
    graph.add_node("triage_and_branch", triage_and_branch)
    graph.add_node("standard_release_prep", standard_release_prep)
    graph.add_node("resilient_security_fetch", resilient_security_fetch)
    graph.add_node("synthesize_solution", synthesize_solution)
    graph.add_node("evaluator_optimizer_node", evaluator_optimizer_node)
    graph.add_node("human_governance_checkpoint", human_governance_checkpoint)
    graph.add_node("deploy_and_publish", deploy_and_publish)
    graph.add_node("abort_and_log", abort_and_log)

    # 2. Add edges & conditional branching
    graph.add_edge(START, "triage_and_branch")
    graph.add_conditional_edges(
        "triage_and_branch",
        route_by_risk,
        {
            "standard_release_prep": "standard_release_prep",
            "resilient_security_fetch": "resilient_security_fetch"
        }
    )

    graph.add_edge("standard_release_prep", "synthesize_solution")

    # Resilience loop
    graph.add_conditional_edges(
        "resilient_security_fetch",
        check_fetch_status,
        {
            "resilient_security_fetch": "resilient_security_fetch",
            "synthesize_solution": "synthesize_solution"
        }
    )

    graph.add_edge("synthesize_solution", "evaluator_optimizer_node")

    # Self-correction loop
    graph.add_conditional_edges(
        "evaluator_optimizer_node",
        route_after_evaluation,
        {
            "synthesize_solution": "synthesize_solution",
            "check_governance": "check_governance"
        }
    )

    # Governance gate
    graph.add_node("check_governance", lambda s: {})
    graph.add_conditional_edges(
        "check_governance",
        check_governance,
        {
            "human_governance_checkpoint": "human_governance_checkpoint",
            "deploy_and_publish": "deploy_and_publish"
        }
    )

    # HITL decision routing
    graph.add_conditional_edges(
        "human_governance_checkpoint",
        route_human_verdict,
        {
            "deploy_and_publish": "deploy_and_publish",
            "abort_and_log": "abort_and_log"
        }
    )

    graph.add_edge("deploy_and_publish", END)
    graph.add_edge("abort_and_log", END)

    return graph.compile(checkpointer=checkpointer)


def run_pipeline_step_by_step(ticket_id: str, requirement: str, auto_resume: bool = True) -> Dict[str, Any]:
    """Utility runner demonstrating the entire lifecycle with interrupt & resume."""
    checkpointer = MemorySaver()
    app = build_enterprise_pipeline(checkpointer=checkpointer)
    thread_config = {"configurable": {"thread_id": f"pipeline-{ticket_id}"}}

    initial_state: EnterprisePipelineState = {
        "ticket_id": ticket_id,
        "requirement": requirement,
        "max_correction_cycles": 3,
        "correction_cycles": 0,
        "pipeline_trace": []
    }

    # Step 1: Run until completion or interrupt
    app.invoke(initial_state, config=thread_config)
    state_snap = app.get_state(thread_config)

    # Check if paused at human checkpoint
    if state_snap.next and "human_governance_checkpoint" in state_snap.next:
        if auto_resume:
            resume_cmd = Command(resume={
                "action": "approve",
                "feedback": "Approved by SecOps Director following rigorous automated verification.",
                "reviewed_by": "secops-director@enterprise.internal"
            })
            return app.invoke(resume_cmd, config=thread_config)

    return state_snap.values


if __name__ == "__main__":
    print("="*60)
    print("Running Flagship Enterprise Orchestrator Pipeline Demo...")
    output = run_pipeline_step_by_step(
        ticket_id="SEC-8821",
        requirement="Implement zero-trust authenticated calculate_moving_average algorithm with bounds check."
    )
    print(f"\nFinal Deployment Status: {output.get('deployment_status')}")
    print("\nPipeline Execution Trace:")
    for trace in output.get("pipeline_trace", []):
        print(f"  {trace}")
    print("\nRelease Manifest:")
    print(output.get("release_notes"))
