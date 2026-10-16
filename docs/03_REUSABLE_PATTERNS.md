# 📦 StateCraft: Catalog of Reusable Orchestration Patterns

This catalog documents the implementation, state contracts, failure modes, and production guidelines for each pattern in StateCraft.

---

## Pattern 1: Dynamic Branching & Conditional Routing

### Purpose
Inspects dynamic properties of state (intent, latency budget, data classification, security tier) to route control flow along specialized execution paths.

### Code File
`src/statecraft/patterns/dynamic_branching.py`

### Key Graph Primitives
- `graph.add_conditional_edges(source, routing_function, path_map)`
- Fan-in pattern: All distinct subpaths converge into a common downstream synthesis node (`format_response`).

### Production Best Practice
- Always provide a fallback default in the conditional routing function. Never assume the LLM classification output is strictly valid JSON without error handling.

---

## Pattern 2: Self-Correction & Evaluator-Optimizer Loop

### Purpose
Eliminates hallucinated code, broken syntax, and failing edge cases through autonomous reflection and iterative repair against automated unit tests.

### Code File
`src/statecraft/patterns/self_correction.py`

### Key Graph Primitives
- Bounded cycle loop: `check_evaluation` checks `iterations < max_iterations`.
- Monotonic feedback history: `feedback_history: Annotated[List[CodeFeedback], append_list]`.

### Production Best Practice
- **Guard against runaway costs**: Every cyclic graph **MUST** have an explicit termination condition bound (`max_iterations`).
- **Provide actionable feedback**: Do not simply tell the LLM "it failed". Pass stdout, stderr, AST line numbers, and assertion diffs so the model has actionable gradient to correct the issue.

---

## Pattern 3: Resilience, Retries & Fallback Circuit

### Purpose
Tolerates transient 429 rate limits, 503 gateway outages, and network jitter without crashing the agentic workflow.

### Code File
`src/statecraft/patterns/resilience_retries.py`

### Key Graph Primitives
- Exponential backoff loop inside state.
- Circuit breaker state channel: `circuit_state: Literal["CLOSED", "HALF_OPEN", "OPEN"]`.
- Graceful degradation node (`activate_fallback`) serving stale L2 cache.

### Production Best Practice
- In high-throughput environments, combine state-level retries with distributed caching (e.g. Redis) to ensure that if a remote service goes dark, user-facing latency does not spike infinitely.

---

## Pattern 4: Human-in-the-Loop (HITL) Checkpoints & Time-Travel

### Purpose
Provides executive and safety governance over high-risk actions by pausing execution, storing state, and awaiting human review.

### Code File
`src/statecraft/patterns/human_in_the_loop.py`

### Key Graph Primitives
- `interrupt(payload)`: Pauses graph and persists to checkpointer.
- `Command(resume=payload)`: Resumes execution with external inputs.
- `app.get_state(config)` and `app.get_state_history(config)`.

### Production Best Practice
- Structure the interrupt payload clearly with context, proposed action, and actionable options (`approve`, `edit`, `reject`).
- Allow the human reviewer to directly edit the state content rather than forcing them to write prompts for the LLM to re-try.

---

## Pattern 5: Hierarchical Supervisor & Multi-Agent Subgraphs

### Purpose
Orchestrates multiple specialized subagents under a central coordinator to solve complex, multi-faceted tasks.

### Code File
`src/statecraft/patterns/hierarchical_supervisor.py`

### Key Graph Primitives
- Supervisor decision node routing to worker sub-nodes.
- Worker return edges looping back to the supervisor.
- Terminal synthesis node generating a consolidated briefing when all subtasks are finished.

### Production Best Practice
- Keep worker subagents narrowly specialized with domain-specific tool access.
- Restrict supervisor state visibility to task summaries rather than passing entire conversational contexts to prevent context bloat.
