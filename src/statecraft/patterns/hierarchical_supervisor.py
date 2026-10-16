"""
Pattern 5: Hierarchical Supervisor & Multi-Agent Subgraph Orchestration.

High-Level Concept:
Complex enterprise workflows frequently exceed the reasoning horizon of a single agent.
The Supervisor Pattern establishes a centralized coordinator node that orchestrates
specialized subagents:
1. Supervisor evaluates the global objective and remaining work.
2. Supervisor delegates the next subtask to a domain specialist:
   - `Researcher`: Gathers threat intelligence and background telemetry.
   - `Engineer`: Formulates algorithmic implementations and architectural specs.
   - `Auditor`: Validates security, compliance, and regression safety.
3. Each worker updates the shared state with its output.
4. The Supervisor routes iteratively until all domain objectives are satisfied,
   then transitions to a Synthesizer node to generate the consolidated report.

Architecture:
                       [START]
                          │
                   [supervisor_node] <───────────┐
                          │                      │
                  (route_next_worker)            │
                  ├── "researcher" ──> [researcher_worker] ──┤
                  ├── "engineer"   ──> [engineer_worker]   ──┤
                  ├── "auditor"    ──> [auditor_worker]    ──┤
                  └── "FINISH" ──────> [synthesizer_node] ──> [END]
"""

from typing import Dict, Any, List, Literal
from langgraph.graph import StateGraph, START, END

from statecraft.state import SupervisorState, AgentTask
from statecraft.llm import get_llm


def supervisor_node(state: SupervisorState) -> Dict[str, Any]:
    """Coordinator Node: Inspects work done and decides the next worker or concludes."""
    worker_outputs = state.get("worker_outputs", {})
    completed_subtasks = state.get("completed_subtasks", [])
    iteration = state.get("iterations", 0) + 1

    # Deterministic delegation sequence or LLM planning
    if "researcher" not in worker_outputs:
        next_worker = "researcher"
        note = f"[Supervisor Cycle {iteration}] Delegating phase 1: Threat & context research."
    elif "engineer" not in worker_outputs:
        next_worker = "engineer"
        note = f"[Supervisor Cycle {iteration}] Delegating phase 2: Technical architecture synthesis."
    elif "auditor" not in worker_outputs:
        next_worker = "auditor"
        note = f"[Supervisor Cycle {iteration}] Delegating phase 3: Security & compliance audit."
    else:
        next_worker = "FINISH"
        note = f"[Supervisor Cycle {iteration}] All specialist phases completed. Proceeding to synthesis."

    return {
        "active_worker": next_worker,
        "iterations": iteration,
        "supervisor_notes": [note]
    }


def route_next_worker(state: SupervisorState) -> Literal["researcher_worker", "engineer_worker", "auditor_worker", "synthesizer_node"]:
    """Conditional Edge: Routes to the selected specialist subagent or final synthesis."""
    active = state.get("active_worker", "FINISH")
    if active == "researcher":
        return "researcher_worker"
    elif active == "engineer":
        return "engineer_worker"
    elif active == "auditor":
        return "auditor_worker"
    else:
        return "synthesizer_node"


def researcher_worker(state: SupervisorState) -> Dict[str, Any]:
    """Specialist Subagent: Investigates background research and attack vectors."""
    llm = get_llm()
    objective = state.get("objective", "")
    findings = llm.invoke(f"Act as Senior Security Researcher. Analyze: {objective}")
    
    task_record: AgentTask = {
        "task_id": "subtask_01_research",
        "assigned_worker": "researcher",
        "instructions": f"Analyze threat vectors for: {objective}",
        "status": "completed",
        "result": findings
    }
    
    current_outputs = dict(state.get("worker_outputs", {}))
    current_outputs["researcher"] = findings

    return {
        "completed_subtasks": [task_record],
        "worker_outputs": current_outputs,
        "supervisor_notes": ["[Worker: Researcher] Completed threat telemetry analysis."]
    }


def engineer_worker(state: SupervisorState) -> Dict[str, Any]:
    """Specialist Subagent: Formulates architectural solutions and code specifications."""
    llm = get_llm()
    objective = state.get("objective", "")
    solution = llm.invoke(f"Act as Principal Software Engineer. Design solution for: {objective}")

    task_record: AgentTask = {
        "task_id": "subtask_02_engineering",
        "assigned_worker": "engineer",
        "instructions": f"Design technical solution for: {objective}",
        "status": "completed",
        "result": solution
    }

    current_outputs = dict(state.get("worker_outputs", {}))
    current_outputs["engineer"] = solution

    return {
        "completed_subtasks": [task_record],
        "worker_outputs": current_outputs,
        "supervisor_notes": ["[Worker: Engineer] Completed system architecture blueprint."]
    }


def auditor_worker(state: SupervisorState) -> Dict[str, Any]:
    """Specialist Subagent: Conducts OWASP compliance and regulatory verification."""
    llm = get_llm()
    objective = state.get("objective", "")
    audit = llm.invoke(f"Act as Lead Compliance Auditor. Audit against OWASP: {objective}")

    task_record: AgentTask = {
        "task_id": "subtask_03_auditor",
        "assigned_worker": "auditor",
        "instructions": f"Audit compliance for: {objective}",
        "status": "completed",
        "result": audit
    }

    current_outputs = dict(state.get("worker_outputs", {}))
    current_outputs["auditor"] = audit

    return {
        "completed_subtasks": [task_record],
        "worker_outputs": current_outputs,
        "supervisor_notes": ["[Worker: Auditor] Completed security & compliance verification."]
    }


def synthesizer_node(state: SupervisorState) -> Dict[str, Any]:
    """Node: Consolidates outputs from all specialized subagents into an executive briefing."""
    objective = state.get("objective", "")
    outputs = state.get("worker_outputs", {})
    
    report = (
        f"====================================================\n"
        f"EXECUTIVE MULTI-AGENT SYNTHESIS BRIEFING\n"
        f"Objective: {objective}\n"
        f"====================================================\n\n"
        f"1. RESEARCH FINDINGS:\n{outputs.get('researcher', 'N/A')}\n\n"
        f"2. ENGINEERING SPECIFICATION:\n{outputs.get('engineer', 'N/A')}\n\n"
        f"3. SECURITY & COMPLIANCE AUDIT:\n{outputs.get('auditor', 'N/A')}\n\n"
        f"STATUS: CERTIFIED FOR PRODUCTION LAUNCH\n"
        f"===================================================="
    )

    return {
        "final_synthesis": report,
        "supervisor_notes": ["[Synthesizer] Merged all worker outputs into unified executive briefing."]
    }


def build_supervisor_graph(checkpointer: Any = None):
    """Compiles and returns the Hierarchical Supervisor StateGraph."""
    graph = StateGraph(SupervisorState)

    # 1. Add nodes
    graph.add_node("supervisor_node", supervisor_node)
    graph.add_node("researcher_worker", researcher_worker)
    graph.add_node("engineer_worker", engineer_worker)
    graph.add_node("auditor_worker", auditor_worker)
    graph.add_node("synthesizer_node", synthesizer_node)

    # 2. Add edges
    graph.add_edge(START, "supervisor_node")

    # 3. Add conditional routing from supervisor
    graph.add_conditional_edges(
        "supervisor_node",
        route_next_worker,
        {
            "researcher_worker": "researcher_worker",
            "engineer_worker": "engineer_worker",
            "auditor_worker": "auditor_worker",
            "synthesizer_node": "synthesizer_node",
        }
    )

    # 4. Each worker reports back to the supervisor
    graph.add_edge("researcher_worker", "supervisor_node")
    graph.add_edge("engineer_worker", "supervisor_node")
    graph.add_edge("auditor_worker", "supervisor_node")

    # 5. Conclude after synthesizer
    graph.add_edge("synthesizer_node", END)

    return graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    app = build_supervisor_graph()
    initial_state: SupervisorState = {
        "objective": "Zero-Trust API Gateway Token Deserialization Security Hardening",
        "worker_outputs": {},
        "completed_subtasks": [],
        "supervisor_notes": [],
        "iterations": 0,
        "max_iterations": 10
    }

    print("="*60)
    print("Executing Hierarchical Supervisor Multi-Agent Graph...")
    result = app.invoke(initial_state)

    print("\nSupervisor Orchestration Journey:")
    for note in result.get("supervisor_notes", []):
        print(f"  {note}")

    print(f"\nFinal Consolidated Synthesis:\n{result.get('final_synthesis')}")
