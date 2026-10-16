"""
Pattern 1: Dynamic Branching & Conditional Routing.

High-Level Concept:
In linear chains, every prompt travels through the identical set of steps regardless
of complexity, intent, or risk. Stateful graphs unlock *conditional routing*—inspecting
the intermediate state and dynamically directing execution down specialized subpaths,
including fast-paths for simple queries and deep-verification paths for high-risk inputs.

Architecture:
               [START]
                  │
          [classify_and_triage]
                  │
        (conditional router)
        ├── if security / high risk ────> [deep_security_audit] ──┐
        ├── if technical / medium risk ──> [technical_solver]   ──┤
        ├── if billing ──────────────────> [billing_specialist] ──┼──> [format_response] ──> [END]
        └── else (standard/low risk) ────> [fast_path_cache]    ──┘
"""

import json
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from statecraft.state import BranchingState
from statecraft.llm import get_llm


def classify_and_triage(state: BranchingState) -> Dict[str, Any]:
    """Node: Analyzes query intent, classifies category, and estimates complexity."""
    query = state.get("query", "")
    llm = get_llm()
    
    prompt = f"Classify the following query and provide JSON with 'category' (billing|technical|security|general) and 'complexity_score' (0.0-1.0): '{query}'"
    raw_response = llm.invoke(prompt, context={"query": query})
    
    try:
        data = json.loads(raw_response)
        category = data.get("category", "general")
        complexity = float(data.get("complexity_score", 0.3))
    except Exception:
        # Fallback heuristic
        if "security" in query.lower() or "auth" in query.lower():
            category = "security"
            complexity = 0.85
        elif "bug" in query.lower() or "crash" in query.lower():
            category = "technical"
            complexity = 0.65
        elif "invoice" in query.lower() or "pay" in query.lower():
            category = "billing"
            complexity = 0.30
        else:
            category = "general"
            complexity = 0.15

    return {
        "category": category,
        "complexity_score": complexity,
        "execution_path": ["classify_and_triage"]
    }


def route_query(state: BranchingState) -> Literal["deep_security_audit", "technical_solver", "billing_specialist", "fast_path_cache"]:
    """Conditional Edge: Evaluates state and returns the next destination node."""
    category = state.get("category")
    complexity = state.get("complexity_score", 0.0)
    
    if category == "security" or complexity >= 0.8:
        return "deep_security_audit"
    elif category == "technical" or complexity >= 0.5:
        return "technical_solver"
    elif category == "billing":
        return "billing_specialist"
    else:
        return "fast_path_cache"


def deep_security_audit(state: BranchingState) -> Dict[str, Any]:
    """Specialized Node: Runs multi-layered security evaluation and risk mitigation."""
    query = state.get("query", "")
    return {
        "selected_route": "deep_security_audit",
        "response": f"[SECURITY AUDIT ACTIVE] Performed vulnerability surface scan for query: '{query}'. Cryptographic validation & OWASP compliance verified.",
        "execution_path": ["deep_security_audit"]
    }


def technical_solver(state: BranchingState) -> Dict[str, Any]:
    """Specialized Node: Technical engineering diagnosis and solution generation."""
    query = state.get("query", "")
    return {
        "selected_route": "technical_solver",
        "response": f"[TECHNICAL RESOLUTION] Analyzed stack trace and root cause for '{query}'. Synthesized algorithmic patch with boundary safety checks.",
        "execution_path": ["technical_solver"]
    }


def billing_specialist(state: BranchingState) -> Dict[str, Any]:
    """Specialized Node: Financial reconciliation and subscription policy logic."""
    query = state.get("query", "")
    return {
        "selected_route": "billing_specialist",
        "response": f"[BILLING PORTAL] Verified ledger transaction for '{query}'. PCI-DSS compliant account reconciliation completed.",
        "execution_path": ["billing_specialist"]
    }


def fast_path_cache(state: BranchingState) -> Dict[str, Any]:
    """Specialized Node: Low-latency fast-path for standard informational queries."""
    query = state.get("query", "")
    return {
        "selected_route": "fast_path_cache",
        "response": f"[FAST-PATH CACHE HIT] Standard answer generated with sub-10ms routing latency for query: '{query}'.",
        "execution_path": ["fast_path_cache"]
    }


def format_response(state: BranchingState) -> Dict[str, Any]:
    """Convergent Fan-In Node: Formats telemetry and metadata before concluding."""
    route = state.get("selected_route", "unknown")
    complexity = state.get("complexity_score", 0.0)
    raw_resp = state.get("response", "")
    
    final_output = f"Result (Route: {route} | Complexity: {complexity:.2f})\n{raw_resp}"
    return {
        "response": final_output,
        "execution_path": ["format_response"]
    }


def build_branching_graph(checkpointer: Any = None):
    """Compiles and returns the Dynamic Branching StateGraph."""
    graph = StateGraph(BranchingState)

    # 1. Register nodes
    graph.add_node("classify_and_triage", classify_and_triage)
    graph.add_node("deep_security_audit", deep_security_audit)
    graph.add_node("technical_solver", technical_solver)
    graph.add_node("billing_specialist", billing_specialist)
    graph.add_node("fast_path_cache", fast_path_cache)
    graph.add_node("format_response", format_response)

    # 2. Add edges
    graph.add_edge(START, "classify_and_triage")

    # 3. Add conditional routing edges
    graph.add_conditional_edges(
        "classify_and_triage",
        route_query,
        {
            "deep_security_audit": "deep_security_audit",
            "technical_solver": "technical_solver",
            "billing_specialist": "billing_specialist",
            "fast_path_cache": "fast_path_cache",
        }
    )

    # 4. Fan-in: all branches converge on format_response
    graph.add_edge("deep_security_audit", "format_response")
    graph.add_edge("technical_solver", "format_response")
    graph.add_edge("billing_specialist", "format_response")
    graph.add_edge("fast_path_cache", "format_response")
    graph.add_edge("format_response", END)

    return graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    app = build_branching_graph()
    sample_queries = [
        "How do I fix a zero-day auth bypass vulnerability in our API?",
        "Our service has a memory leak when parsing 100k records",
        "Can I get a refund for my duplicate subscription charge?",
        "What are your business hours on weekends?"
    ]
    for q in sample_queries:
        out = app.invoke({"query": q})
        print("\n" + "="*60)
        print(f"Query: {q}")
        print(f"Path Taken: {' -> '.join(out['execution_path'])}")
        print(f"Output:\n{out['response']}")
