"""
FastAPI Server for StateCraft Stateful Agentic Orchestration.

Exposes REST API endpoints for:
- Initiating stateful workflow threads
- Intercepting HITL interrupt checkpoints
- Resuming threads with human reviewer decisions
- Inspecting graph state and checkpoint histories
"""

from typing import Dict, Any, Optional, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from statecraft.patterns.dynamic_branching import build_branching_graph
from statecraft.patterns.self_correction import build_self_correction_graph
from statecraft.patterns.resilience_retries import build_resilience_graph
from statecraft.patterns.human_in_the_loop import build_hitl_graph
from statecraft.orchestrator.enterprise_pipeline import build_enterprise_pipeline

app = FastAPI(
    title="StateCraft Workflow Orchestration API",
    description="Production-grade stateful agent orchestration with LangGraph",
    version="1.0.0"
)

# Global in-memory checkpointer shared across requests
GLOBAL_CHECKPOINTER = MemorySaver()
ENTERPRISE_APP = build_enterprise_pipeline(checkpointer=GLOBAL_CHECKPOINTER)
HITL_APP = build_hitl_graph(checkpointer=GLOBAL_CHECKPOINTER)


class RunPipelineRequest(BaseModel):
    ticket_id: str = Field(default="SEC-9001", description="Unique ticket identifier")
    requirement: str = Field(default="Implement calculate_moving_average algorithm", description="Feature or bug requirement")
    thread_id: Optional[str] = Field(default=None, description="Optional thread identifier for state persistence")


class ResumePipelineRequest(BaseModel):
    thread_id: str = Field(..., description="The thread identifier paused at a checkpoint")
    action: Literal["approve", "edit", "reject"] = Field(..., description="Human review action")
    feedback: Optional[str] = Field(default="Approved via API", description="Reviewer comments")
    edited_content: Optional[str] = Field(default=None, description="Optional edited content/code")
    reviewed_by: Optional[str] = Field(default="security-lead@api.internal", description="Reviewer email/identity")


class BranchingRequest(BaseModel):
    query: str = Field(..., description="User query to route dynamically")


class SelfCorrectionRequest(BaseModel):
    task: str = Field(default="Write calculate_moving_average(numbers: list[float], window_size: int) -> list[float]")
    max_iterations: int = Field(default=3)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "StateCraft Orchestration Engine",
        "langgraph_version": "1.2.x"
    }


@app.post("/api/v1/orchestrator/run")
def run_orchestrator(req: RunPipelineRequest):
    thread_id = req.thread_id or f"thread-{req.ticket_id}"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "ticket_id": req.ticket_id,
        "requirement": req.requirement,
        "max_correction_cycles": 3,
        "correction_cycles": 0,
        "pipeline_trace": []
    }

    ENTERPRISE_APP.invoke(initial_state, config=config)
    state_snap = ENTERPRISE_APP.get_state(config)

    is_paused = bool(state_snap.next and "human_governance_checkpoint" in state_snap.next)
    interrupt_payload = None
    if is_paused and state_snap.tasks and state_snap.tasks[0].interrupts:
        interrupt_payload = state_snap.tasks[0].interrupts[0].value

    return {
        "thread_id": thread_id,
        "status": "PAUSED_AT_CHECKPOINT" if is_paused else state_snap.values.get("deployment_status", "UNKNOWN"),
        "is_paused": is_paused,
        "interrupt_payload": interrupt_payload,
        "pipeline_trace": state_snap.values.get("pipeline_trace", []),
        "state_snapshot": state_snap.values
    }


@app.post("/api/v1/orchestrator/resume")
def resume_orchestrator(req: ResumePipelineRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    state_snap = ENTERPRISE_APP.get_state(config)

    if not state_snap.next:
        raise HTTPException(status_code=400, detail=f"Thread '{req.thread_id}' is not currently paused at a checkpoint.")

    resume_cmd = Command(resume={
        "action": req.action,
        "feedback": req.feedback,
        "edited_content": req.edited_content,
        "reviewed_by": req.reviewed_by
    })

    final_result = ENTERPRISE_APP.invoke(resume_cmd, config=config)
    return {
        "thread_id": req.thread_id,
        "status": final_result.get("deployment_status"),
        "release_notes": final_result.get("release_notes"),
        "pipeline_trace": final_result.get("pipeline_trace", [])
    }


@app.get("/api/v1/orchestrator/state/{thread_id}")
def get_thread_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    snap = ENTERPRISE_APP.get_state(config)
    if not snap or not snap.values:
        raise HTTPException(status_code=404, detail=f"Thread '{thread_id}' not found.")
    
    return {
        "thread_id": thread_id,
        "next_nodes": snap.next,
        "values": snap.values
    }


@app.post("/api/v1/patterns/branching")
def pattern_branching(req: BranchingRequest):
    graph = build_branching_graph()
    result = graph.invoke({"query": req.query})
    return {
        "query": req.query,
        "category": result.get("category"),
        "complexity_score": result.get("complexity_score"),
        "selected_route": result.get("selected_route"),
        "execution_path": result.get("execution_path"),
        "response": result.get("response")
    }


@app.post("/api/v1/patterns/self-correction")
def pattern_self_correction(req: SelfCorrectionRequest):
    graph = build_self_correction_graph()
    result = graph.invoke({
        "task": req.task,
        "max_iterations": req.max_iterations,
        "iterations": 0,
        "logs": []
    })
    return {
        "status": result.get("status"),
        "iterations": result.get("iterations"),
        "logs": result.get("logs"),
        "code": result.get("code")
    }
