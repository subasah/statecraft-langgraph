"""
State definitions and reducers for StateCraft workflows.

In LangGraph, State acts as the shared blackboard and communication channel
between nodes in the computation graph. Each node receives the current state,
executes logic, and returns a dictionary of state updates.

Key Concepts Demonstrated:
1. TypedDict state schemas with precise field typing.
2. Channel Reducers (e.g. Annotated[list, operator.add]) for monotonic event accumulation.
3. Checkpoint-safe serializable data structures.
"""

from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict
import operator


def append_list(current: List[Any], new: Any) -> List[Any]:
    """Reducer that appends item(s) to a list without mutating the original state.
    
    Handles both single item appends and batch list extensions.
    """
    if current is None:
        current = []
    if isinstance(new, list):
        return current + new
    return current + [new]


# ---------------------------------------------------------------------------
# Pattern 1: Dynamic Branching State
# ---------------------------------------------------------------------------
class BranchingState(TypedDict, total=False):
    """State for dynamic routing based on query complexity and classification."""
    query: str
    category: Literal["billing", "technical", "security", "general"]
    complexity_score: float  # 0.0 to 1.0
    selected_route: str
    execution_path: Annotated[List[str], append_list]
    response: str
    metadata: Dict[str, Any]


# ---------------------------------------------------------------------------
# Pattern 2: Self-Correction / Evaluator-Optimizer State
# ---------------------------------------------------------------------------
class CodeFeedback(TypedDict):
    """Structured feedback from the evaluator node."""
    passed: bool
    syntax_valid: bool
    tests_passed: int
    total_tests: int
    errors: List[str]
    critique: str


class SelfCorrectionState(TypedDict, total=False):
    """State for the generator-evaluator reflection and self-correction loop."""
    task: str
    code: str
    test_suite: str
    feedback: Optional[CodeFeedback]
    feedback_history: Annotated[List[CodeFeedback], append_list]
    iterations: int
    max_iterations: int
    is_success: bool
    status: str
    logs: Annotated[List[str], append_list]


# ---------------------------------------------------------------------------
# Pattern 3: Resilience & Retry State
# ---------------------------------------------------------------------------
class ResilienceState(TypedDict, total=False):
    """State for resilient execution with transient faults and fallback paths."""
    endpoint: str
    request_payload: Dict[str, Any]
    attempt: int
    max_retries: int
    backoff_seconds: float
    circuit_state: Literal["CLOSED", "HALF_OPEN", "OPEN"]
    failures_encountered: Annotated[List[str], append_list]
    fallback_used: bool
    data: Optional[Dict[str, Any]]
    execution_trace: Annotated[List[str], append_list]


# ---------------------------------------------------------------------------
# Pattern 4: Human-in-the-Loop (HITL) State
# ---------------------------------------------------------------------------
class HumanReviewDecision(TypedDict, total=False):
    """User review response provided during checkpoint resumption."""
    action: Literal["approve", "reject", "edit"]
    feedback: Optional[str]
    edited_content: Optional[str]
    reviewed_by: Optional[str]


class HumanInTheLoopState(TypedDict, total=False):
    """State for human-supervised workflows with interruptible checkpoints."""
    draft_title: str
    draft_body: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    automated_safety_check: bool
    safety_notes: List[str]
    human_review_required: bool
    review_decision: Optional[HumanReviewDecision]
    published_output: Optional[str]
    status: Literal["drafting", "awaiting_approval", "approved", "rejected", "published"]
    audit_trail: Annotated[List[str], append_list]


# ---------------------------------------------------------------------------
# Pattern 5: Hierarchical Supervisor State
# ---------------------------------------------------------------------------
class AgentTask(TypedDict):
    task_id: str
    assigned_worker: str
    instructions: str
    status: Literal["pending", "in_progress", "completed", "failed"]
    result: Optional[str]


class SupervisorState(TypedDict, total=False):
    """State for hierarchical coordinator delegating to specialized subagents."""
    objective: str
    active_worker: Optional[str]
    completed_subtasks: Annotated[List[AgentTask], append_list]
    worker_outputs: Dict[str, str]
    supervisor_notes: Annotated[List[str], append_list]
    final_synthesis: Optional[str]
    iterations: int
    max_iterations: int


# ---------------------------------------------------------------------------
# Flagship End-to-End Enterprise Orchestration State
# ---------------------------------------------------------------------------
class EnterprisePipelineState(TypedDict, total=False):
    """Unifies Branching, Self-Correction, Retries, and HITL into an enterprise pipeline.
    
    Scenario: Autonomous Feature & Security Remediation Release Pipeline.
    1. Triage & Risk Branching (Low-risk automated vs High-risk deep analysis)
    2. Resilient API/Tool Fetch (Retries on flaky external services)
    3. Code & Test Synthesis
    4. Evaluator-Optimizer Self-Correction Loop
    5. Human-in-the-Loop Checkpoint (Security/Executive sign-off)
    6. Deployment & Artifact Release
    """
    ticket_id: str
    requirement: str
    risk_tier: Literal["TIER_1_STANDARD", "TIER_2_ELEVATED", "TIER_3_CRITICAL"]
    branch_taken: str
    resilient_fetch_attempts: int
    specification: str
    code_solution: str
    test_code: str
    evaluator_feedback: Optional[CodeFeedback]
    correction_cycles: int
    max_correction_cycles: int
    requires_human_signoff: bool
    human_decision: Optional[HumanReviewDecision]
    deployment_status: Literal["PENDING", "TRIAGED", "CODING", "REVIEW", "DEPLOYED", "ABORTED"]
    release_notes: str
    pipeline_trace: Annotated[List[str], append_list]
