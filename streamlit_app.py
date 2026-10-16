"""
StateCraft: Streamlit Visual Studio & Recruiter Showcase.

Interactive dashboard to run, visualize, inspect, and step through:
- Pattern 1: Dynamic Branching & Conditional Routing
- Pattern 2: Self-Correction & Evaluator-Optimizer Loop
- Pattern 3: Resilience, Retries & Fallback Circuit
- Pattern 4: Human-in-the-Loop Checkpoints & Time-Travel
- Pattern 5: Hierarchical Supervisor Multi-Agent
- Flagship: Autonomous Enterprise Release Pipeline
- Recruiter Talking Points & STAR Cheat Sheet
"""

import time
import json
import streamlit as st
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from statecraft.patterns.dynamic_branching import build_branching_graph
from statecraft.patterns.self_correction import build_self_correction_graph
from statecraft.patterns.resilience_retries import build_resilience_graph
from statecraft.patterns.human_in_the_loop import build_hitl_graph
from statecraft.patterns.hierarchical_supervisor import build_supervisor_graph
from statecraft.orchestrator.enterprise_pipeline import build_enterprise_pipeline

st.set_page_config(
    page_title="StateCraft | LangGraph Stateful Workflows",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #616161;
        margin-bottom: 1.5rem;
    }
    .badge-card {
        padding: 0.8rem;
        border-radius: 8px;
        background-color: #f8f9fa;
        border-left: 4px solid #1E88E5;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("⚡ StateCraft Studio")
st.sidebar.caption("LangGraph Production Orchestration Engine")

tab_choice = st.sidebar.radio(
    "Select Workflow / Pattern:",
    [
        "🚀 Flagship: Enterprise Pipeline",
        "🔀 1. Dynamic Branching",
        "🔄 2. Self-Correction Loop",
        "🛡️ 3. Resilience & Retries",
        "👤 4. Human-in-the-Loop",
        "👑 5. Hierarchical Supervisor",
        "💼 Recruiter & Architecture Guide"
    ]
)

# Global Session Memory for HITL persistence in Streamlit
if "hitl_checkpointer" not in st.session_state:
    st.session_state.hitl_checkpointer = MemorySaver()
    st.session_state.hitl_app = build_hitl_graph(checkpointer=st.session_state.hitl_checkpointer)

if "enterprise_checkpointer" not in st.session_state:
    st.session_state.enterprise_checkpointer = MemorySaver()
    st.session_state.enterprise_app = build_enterprise_pipeline(checkpointer=st.session_state.enterprise_checkpointer)


# ---------------------------------------------------------------------------
# TAB: FLAGSHIP ENTERPRISE PIPELINE
# ---------------------------------------------------------------------------
if tab_choice == "🚀 Flagship: Enterprise Pipeline":
    st.markdown('<div class="main-header">Autonomous Software & Security Release Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Unifies Branching, Resilient Ingestion, Evaluator Self-Correction, and HITL Governance into a production workflow.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Ticket Submission")
        ticket_id = st.text_input("Ticket ID", value="SEC-9042")
        requirement = st.text_area(
            "Feature / Security Requirement",
            value="Implement zero-trust authenticated calculate_moving_average algorithm with memory bounds protection.",
            height=100
        )
        
        thread_id = f"enterprise-{ticket_id}"
        config = {"configurable": {"thread_id": thread_id}}

        if st.button("▶️ Launch Pipeline", type="primary"):
            st.session_state.pipeline_thread_id = thread_id
            with st.spinner("Executing pipeline through triage, resilience, and self-correction..."):
                initial_state = {
                    "ticket_id": ticket_id,
                    "requirement": requirement,
                    "max_correction_cycles": 3,
                    "correction_cycles": 0,
                    "pipeline_trace": []
                }
                st.session_state.enterprise_app.invoke(initial_state, config=config)
                st.rerun()

    with col2:
        st.subheader("2. Live State & HITL Checkpoint Gate")
        current_thread = getattr(st.session_state, "pipeline_thread_id", f"enterprise-{ticket_id}")
        config = {"configurable": {"thread_id": current_thread}}
        state_snap = st.session_state.enterprise_app.get_state(config)

        if state_snap and state_snap.values:
            status = state_snap.values.get("deployment_status", "UNKNOWN")
            tier = state_snap.values.get("risk_tier", "N/A")
            cycles = state_snap.values.get("correction_cycles", 0)

            st.info(f"**Ticket:** `{ticket_id}` | **Risk Tier:** `{tier}` | **Status:** `{status}` | **Cycles:** `{cycles}`")

            # Check if paused at interrupt checkpoint
            if state_snap.next and "human_governance_checkpoint" in state_snap.next:
                st.warning("⚠️ **PIPELINE PAUSED: Human Governance Approval Required**")
                interrupt_val = state_snap.tasks[0].interrupts[0].value
                st.json(interrupt_val)

                st.markdown("### Reviewer Action")
                action = st.radio("Decision", ["approve", "edit", "reject"], horizontal=True)
                feedback = st.text_input("Reviewer Notes", value="Security criteria satisfied via automated tests.")
                edited_code = None
                if action == "edit":
                    edited_code = st.text_area("Edit Candidate Code", value=state_snap.values.get("code_solution", ""))

                if st.button("Submit Decision & Resume Execution (Command.resume)"):
                    resume_cmd = Command(resume={
                        "action": action,
                        "feedback": feedback,
                        "edited_content": edited_code,
                        "reviewed_by": "secops-director@enterprise.internal"
                    })
                    with st.spinner("Resuming pipeline with human decision..."):
                        st.session_state.enterprise_app.invoke(resume_cmd, config=config)
                        st.rerun()

            elif status == "DEPLOYED":
                st.success("🎉 **Release LIVE in Production!**")
                st.code(state_snap.values.get("release_notes", ""), language="text")

            st.markdown("#### Execution Trace")
            for trace in state_snap.values.get("pipeline_trace", []):
                st.write(f"- `{trace}`")


# ---------------------------------------------------------------------------
# TAB 1: DYNAMIC BRANCHING
# ---------------------------------------------------------------------------
elif tab_choice == "🔀 1. Dynamic Branching":
    st.markdown('<div class="main-header">Pattern 1: Dynamic Branching & Conditional Routing</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Routes queries to specialized sub-graphs based on intent classification and risk scoring.</div>', unsafe_allow_html=True)

    sample_queries = [
        "How do I patch a critical authentication bypass zero-day CVE?",
        "Our backend crashed with a memory leak in the stream processor",
        "Need refund for a duplicate invoice on subscription account",
        "What are your standard support operating hours?"
    ]
    query = st.selectbox("Select Sample Query or Type Custom:", sample_queries)

    if st.button("Route Query"):
        app = build_branching_graph()
        with st.spinner("Analyzing intent and routing..."):
            res = app.invoke({"query": query})
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Classified Category", res.get("category", "").upper())
        c2.metric("Complexity Score", f"{res.get('complexity_score', 0):.2f}")
        c3.metric("Selected Route Node", res.get("selected_route"))

        st.markdown("#### Execution Path")
        st.code(" ➡️ ".join(res.get("execution_path", [])), language="text")

        st.markdown("#### Node Output")
        st.info(res.get("response"))


# ---------------------------------------------------------------------------
# TAB 2: SELF-CORRECTION LOOP
# ---------------------------------------------------------------------------
elif tab_choice == "🔄 2. Self-Correction Loop":
    st.markdown('<div class="main-header">Pattern 2: Self-Correction & Evaluator-Optimizer Loop</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Autonomous reflection cycle: Generator generates code -> Evaluator tests it -> Feeds critique back -> Re-generates until passing.</div>', unsafe_allow_html=True)

    task_desc = st.text_input("Coding Task", value="Write calculate_moving_average(numbers: list[float], window_size: int) -> list[float]")
    max_iter = st.slider("Max Iteration Budget", min_value=1, max_value=5, value=3)

    if st.button("Run Self-Correction Loop"):
        app = build_self_correction_graph()
        with st.spinner("Running generator-evaluator reflection cycles..."):
            res = app.invoke({
                "task": task_desc,
                "max_iterations": max_iter,
                "iterations": 0,
                "logs": []
            })

        st.success(f"Execution Concluded: Status = {res.get('status')} ({res.get('iterations')} cycles)")
        
        st.markdown("#### Step-by-Step Reflection Logs")
        for log in res.get("logs", []):
            st.write(f"- `{log}`")

        st.markdown("#### Final Synthesized Code")
        st.code(res.get("code", ""), language="python")


# ---------------------------------------------------------------------------
# TAB 3: RESILIENCE & RETRIES
# ---------------------------------------------------------------------------
elif tab_choice == "🛡️ 3. Resilience & Retries":
    st.markdown('<div class="main-header">Pattern 3: Resilience, Retries & Fallback Circuit</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Transient fault tolerance with exponential backoff and circuit-breaker fallback cache.</div>', unsafe_allow_html=True)

    scenario = st.radio("Choose Simulated Service State:", [
        "Flaky API (Fails 429 twice, then recovers on attempt 3)",
        "Outage / Down API (Fails 503 repeatedly -> Trips Circuit Breaker to L2 Cache)",
        "Healthy API (Succeeds immediately on attempt 1)"
    ])

    endpoint_map = {
        "Flaky API (Fails 429 twice, then recovers on attempt 3)": "https://api.internal/flaky_telemetry",
        "Outage / Down API (Fails 503 repeatedly -> Trips Circuit Breaker to L2 Cache)": "https://api.internal/down_service",
        "Healthy API (Succeeds immediately on attempt 1)": "https://api.internal/healthy_telemetry"
    }

    if st.button("Execute Resilient Request"):
        app = build_resilience_graph()
        with st.spinner("Connecting with backoff and circuit protection..."):
            res = app.invoke({
                "endpoint": endpoint_map[scenario],
                "max_retries": 3,
                "attempt": 0,
                "failures_encountered": [],
                "execution_trace": []
            })

        c1, c2, c3 = st.columns(3)
        c1.metric("Attempts Made", res.get("attempt"))
        c2.metric("Fallback Cache Used?", str(res.get("fallback_used")))
        c3.metric("Circuit Breaker State", res.get("circuit_state"))

        st.markdown("#### Request Execution Trace")
        for step in res.get("execution_trace", []):
            st.write(f"- `{step}`")

        st.markdown("#### Resulting Data Payload")
        st.json(res.get("data", {}))


# ---------------------------------------------------------------------------
# TAB 4: HUMAN IN THE LOOP
# ---------------------------------------------------------------------------
elif tab_choice == "👤 4. Human-in-the-Loop":
    st.markdown('<div class="main-header">Pattern 4: Human-in-the-Loop (HITL) & Time-Travel</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">LangGraph native persistence: interrupt() pauses graph, human inspects/edits state, and Command(resume=...) continues.</div>', unsafe_allow_html=True)

    hitl_thread_id = "hitl-demo-thread"
    hitl_config = {"configurable": {"thread_id": hitl_thread_id}}

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Start Supervised Workflow")
        doc_title = st.text_input("Operational Spec Title", value="Global CDN Routing Table Rebalance")
        doc_body = st.text_area("Proposed Operation", value="Re-route APAC traffic through Singapore edge cluster.")
        doc_risk = st.selectbox("Risk Level", ["LOW", "MEDIUM", "HIGH", "CRITICAL"], index=2)

        if st.button("Start Workflow Thread"):
            with st.spinner("Running up to safety checkpoint..."):
                st.session_state.hitl_app.invoke({
                    "draft_title": doc_title,
                    "draft_body": doc_body,
                    "risk_level": doc_risk,
                    "audit_trail": []
                }, config=hitl_config)
                st.rerun()

    with col2:
        st.subheader("2. Reviewer Checkpoint Console")
        hitl_state = st.session_state.hitl_app.get_state(hitl_config)

        if hitl_state and hitl_state.values:
            status = hitl_state.values.get("status")
            st.info(f"**Current Thread Status:** `{status}` | **Next Node:** `{hitl_state.next}`")

            if hitl_state.next and "human_review_checkpoint" in hitl_state.next:
                st.warning("🚨 **INTERRUPT PAUSED AT CHECKPOINT**")
                req_data = hitl_state.tasks[0].interrupts[0].value
                st.write(f"**Draft:** {req_data.get('draft_title')}")
                st.write(f"**Content:** {req_data.get('draft_body')}")

                user_action = st.radio("Action", ["approve", "edit", "reject"])
                user_feedback = st.text_input("Feedback", value="Validated latency impact. Approved.")
                user_edits = None
                if user_action == "edit":
                    user_edits = st.text_area("Edit Content Directly", value=req_data.get("draft_body"))

                if st.button("Submit Decision via Command(resume=...)"):
                    resume_cmd = Command(resume={
                        "action": user_action,
                        "feedback": user_feedback,
                        "edited_content": user_edits,
                        "reviewed_by": "lead.infra@enterprise.internal"
                    })
                    st.session_state.hitl_app.invoke(resume_cmd, config=hitl_config)
                    st.rerun()

            elif status == "published":
                st.success("Published Successfully!")
                st.code(hitl_state.values.get("published_output", ""))

            st.markdown("#### Audit Trail")
            for item in hitl_state.values.get("audit_trail", []):
                st.write(f"- `{item}`")


# ---------------------------------------------------------------------------
# TAB 5: HIERARCHICAL SUPERVISOR
# ---------------------------------------------------------------------------
elif tab_choice == "👑 5. Hierarchical Supervisor":
    st.markdown('<div class="main-header">Pattern 5: Hierarchical Supervisor & Subgraphs</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Centralized coordinator dynamically delegates subtasks to specialized Researcher, Engineer, and Auditor subagents.</div>', unsafe_allow_html=True)

    objective = st.text_input("Global Objective", value="Zero-Trust API Gateway Token Deserialization Security Hardening")

    if st.button("Execute Multi-Agent Supervision"):
        app = build_supervisor_graph()
        with st.spinner("Supervisor orchestrating Researcher, Engineer, and Auditor subagents..."):
            res = app.invoke({
                "objective": objective,
                "worker_outputs": {},
                "completed_subtasks": [],
                "supervisor_notes": [],
                "iterations": 0,
                "max_iterations": 10
            })

        st.subheader("Supervisor Delegation Journey")
        for note in res.get("supervisor_notes", []):
            st.write(f"- `{note}`")

        st.subheader("Consolidated Executive Briefing")
        st.code(res.get("final_synthesis", ""), language="text")


# ---------------------------------------------------------------------------
# TAB: RECRUITER & ARCHITECTURE GUIDE
# ---------------------------------------------------------------------------
else:
    st.markdown('<div class="main-header">Recruiter & Senior AI Engineer Interview Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">System design rationale, STAR framework talking points, and LangGraph architecture principles.</div>', unsafe_allow_html=True)

    with st.expander("📌 1. The 'Elevator Pitch': How to describe this project in 60 seconds", expanded=True):
        st.markdown("""
        > *"In this project, I engineered **StateCraft**, a production-grade orchestration system built on **LangGraph** that solves the major reliability failure modes of autonomous agents.
        > Rather than relying on fragile linear chains or unconstrained ReAct loops, StateCraft implements five core architectural patterns:
        > **Dynamic Intent Branching**, **Evaluator-Optimizer Self-Correction** with AST syntax & unit test verification, **Resilient Exponential Retries with Circuit Breaking**, **Human-in-the-Loop Checkpoints** using LangGraph's `interrupt()` and `Command(resume=...)`, and a **Hierarchical Supervisor** coordinating multi-agent subgraphs.
        > I also unified all five into an autonomous software release and security remediation engine with persistent state checkpointing and time-travel replay."*
        """)

    with st.expander("❓ 2. Why LangGraph over Linear Chains or Standard LangChain DAGs?"):
        st.markdown("""
        - **Cyclic Graphs vs DAGs**: Real-world cognitive workflows require loops (generate -> evaluate -> critique -> fix). Standard DAGs cannot loop without hacky recursive calls. LangGraph is fundamentally a state machine that natively supports cyclic graphs.
        - **First-Class State Reducers**: In LangGraph, state updates are explicit channels with custom reducers (e.g. `Annotated[list, operator.add]` for append-only audit trails), preventing accidental state mutation.
        - **Durable Checkpointing & Human-in-the-Loop**: Workflows can halt asynchronously for hours or days waiting for human review (`interrupt()`), persist to Redis/Postgres/SQLite, and resume seamlessly without losing conversation context or thread state.
        """)

    with st.expander("💡 3. STAR Framework Example: Solving Infinite Agent Loops"):
        st.markdown("""
        - **Situation**: In automated code generation, agents can get stuck in infinite correction loops when failing obscure edge cases, burning excessive API tokens.
        - **Task**: Implement a resilient, bounded self-correction mechanism with guaranteed termination and graceful escalation.
        - **Action**: In StateCraft's `self_correction.py` and `enterprise_pipeline.py`, I designed an Evaluator-Optimizer loop where the graph state tracks iteration counters and explicit error critiques. If the unit test suite fails and `iterations < max_iterations`, it cycles back with targeted feedback. Once `max_iterations` is reached, conditional edges divert to a bounded fallback escalation node.
        - **Result**: 100% loop termination guarantee, zero run-away API costs, and seamless human escalation when code cannot be autonomously resolved.
        """)
