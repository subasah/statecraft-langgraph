"""
Reusable LangGraph Orchestration Patterns.

Exposes:
- build_branching_graph: Dynamic routing and capability branching.
- build_self_correction_graph: Evaluator-Optimizer loop with test runner & reflection.
- build_resilience_graph: Retry policy with exponential backoff & fallback circuit.
- build_hitl_graph: Human-in-the-loop checkpoints, state inspection, and resumption.
- build_supervisor_graph: Hierarchical multi-agent delegation & task synthesis.
"""

from statecraft.patterns.dynamic_branching import build_branching_graph
from statecraft.patterns.self_correction import build_self_correction_graph
from statecraft.patterns.resilience_retries import build_resilience_graph
from statecraft.patterns.human_in_the_loop import build_hitl_graph
from statecraft.patterns.hierarchical_supervisor import build_supervisor_graph

__all__ = [
    "build_branching_graph",
    "build_self_correction_graph",
    "build_resilience_graph",
    "build_hitl_graph",
    "build_supervisor_graph",
]
