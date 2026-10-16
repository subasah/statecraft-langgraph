"""
Pattern 3: Resilience, Transient Fault Tolerance & Fallback Circuit.

High-Level Concept:
In enterprise architectures, agents rely heavily on remote microservices, vector DBs,
and third-party APIs that suffer from transient network partitions, 429 rate limits,
and 503 service outages. A brittle workflow crashes outright.

A production-grade stateful workflow implements:
1. Stateful retry loops with exponential backoff and jitter.
2. Circuit Breaker semantics (CLOSED -> OPEN -> HALF_OPEN).
3. Fallback degradation: When retry budgets are exhausted, execution gracefully
   diverts to a secondary fallback provider or cached artifact instead of failing.

Architecture:
               [START]
                  │
        [call_remote_service] <──────────────┐ (exponential backoff)
                  │                          │
        (check_service_health)               │
        ├── if transient error & attempt < max ─┘
        ├── if success ──────────────> [process_payload] ─────> [END]
        └── if exhausted retries ────> [activate_fallback] ───> [END]
"""

import time
import random
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

from statecraft.state import ResilienceState


def call_remote_service(state: ResilienceState) -> Dict[str, Any]:
    """Node: Attempts execution against an external service, simulating transient errors."""
    endpoint = state.get("endpoint", "https://api.internal.service/v1/telemetry")
    attempt = state.get("attempt", 0) + 1
    max_retries = state.get("max_retries", 3)
    
    # Simulate a realistic transient failure that fails on attempt 1 and 2, but recovers on 3
    # or fails completely if configured to test circuit breaker fallback.
    is_flaky_test = "flaky" in endpoint.lower()
    is_down_test = "down" in endpoint.lower()

    trace_msg = f"[Attempt {attempt}/{max_retries}] Requesting {endpoint}..."

    if is_down_test:
        # Service is completely down: tests circuit breaker fallback
        return {
            "attempt": attempt,
            "failures_encountered": [f"HTTP 503 Service Unavailable at attempt {attempt}"],
            "execution_trace": [trace_msg, f"-> Failed: HTTP 503 (Attempt {attempt})"]
        }
    elif is_flaky_test and attempt < 3:
        # Transient failure (e.g. rate limit HTTP 429)
        return {
            "attempt": attempt,
            "failures_encountered": [f"HTTP 429 Too Many Requests (Transient at attempt {attempt})"],
            "execution_trace": [trace_msg, f"-> Failed: HTTP 429 Rate Limit (Attempt {attempt})"]
        }
    else:
        # Succeeded
        payload = {
            "status": "healthy",
            "cluster_nodes": 12,
            "latency_ms": 42.5,
            "data_records": 1500
        }
        return {
            "attempt": attempt,
            "data": payload,
            "execution_trace": [trace_msg, f"-> Succeeded: 200 OK on attempt {attempt}"]
        }


def check_service_health(state: ResilienceState) -> Literal["call_remote_service", "process_payload", "activate_fallback"]:
    """Conditional Edge: Determines whether to retry, complete, or trip circuit breaker."""
    data = state.get("data")
    attempt = state.get("attempt", 1)
    max_retries = state.get("max_retries", 3)

    if data is not None:
        return "process_payload"
    elif attempt < max_retries:
        # Exponential backoff simulation
        backoff = 0.05 * (2 ** (attempt - 1))
        time.sleep(backoff)
        return "call_remote_service"
    else:
        return "activate_fallback"


def process_payload(state: ResilienceState) -> Dict[str, Any]:
    """Node: Processes successful payload from primary service."""
    data = state.get("data", {})
    return {
        "fallback_used": False,
        "circuit_state": "CLOSED",
        "execution_trace": [f"[Success] Processed fresh payload with {data.get('cluster_nodes', 0)} nodes."]
    }


def activate_fallback(state: ResilienceState) -> Dict[str, Any]:
    """Node: Graceful degradation via fallback cache / synthetic default."""
    failures = state.get("failures_encountered", [])
    cached_payload = {
        "status": "degraded_cached",
        "cluster_nodes": 10,
        "latency_ms": 0.0,
        "data_records": 1200,
        "source": "L2_REDIS_FALLBACK_CACHE"
    }
    return {
        "data": cached_payload,
        "fallback_used": True,
        "circuit_state": "OPEN",
        "execution_trace": [
            f"[Circuit Breaker Tripped] Exhausted retries ({len(failures)} failures). Gracefully served stale L2 cache."
        ]
    }


def build_resilience_graph(checkpointer: Any = None):
    """Compiles and returns the Resilience & Retry StateGraph."""
    graph = StateGraph(ResilienceState)

    # 1. Add nodes
    graph.add_node("call_remote_service", call_remote_service)
    graph.add_node("process_payload", process_payload)
    graph.add_node("activate_fallback", activate_fallback)

    # 2. Add edges
    graph.add_edge(START, "call_remote_service")

    # 3. Add conditional loop edge
    graph.add_conditional_edges(
        "call_remote_service",
        check_service_health,
        {
            "call_remote_service": "call_remote_service",
            "process_payload": "process_payload",
            "activate_fallback": "activate_fallback",
        }
    )

    graph.add_edge("process_payload", END)
    graph.add_edge("activate_fallback", END)

    return graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    app = build_resilience_graph()

    print("="*60)
    print("Scenario A: Flaky Service (Transient Failures -> Recovers on Attempt 3)")
    res_flaky = app.invoke({
        "endpoint": "https://api.internal.service/v1/flaky_telemetry",
        "max_retries": 3,
        "attempt": 0,
        "failures_encountered": [],
        "execution_trace": []
    })
    print(f"Fallback Used: {res_flaky['fallback_used']} | Circuit State: {res_flaky['circuit_state']}")
    for step in res_flaky["execution_trace"]:
        print(f"  {step}")

    print("\n" + "="*60)
    print("Scenario B: Dead Service (Exhausts Retries -> Graceful Fallback Cache)")
    res_dead = app.invoke({
        "endpoint": "https://api.internal.service/v1/down_service",
        "max_retries": 3,
        "attempt": 0,
        "failures_encountered": [],
        "execution_trace": []
    })
    print(f"Fallback Used: {res_dead['fallback_used']} | Circuit State: {res_dead['circuit_state']}")
    print(f"Payload Source: {res_dead['data'].get('source')}")
    for step in res_dead["execution_trace"]:
        print(f"  {step}")
