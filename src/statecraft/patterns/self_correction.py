"""
Pattern 2: Self-Correction & Evaluator-Optimizer Loop.

High-Level Concept:
Single-pass generation often produces brittle solutions containing subtle bugs,
syntax errors, or failed edge cases. The Evaluator-Optimizer pattern introduces
an autonomous critique-and-refine feedback loop:
1. Generator node synthesizes an initial candidate solution.
2. Evaluator node executes automated tests and static analysis.
3. If defects are detected, an error critique is fed back into state, and the
   graph cycles back to the Generator with explicit instructions to fix the failure.
4. The loop is strictly bounded by `max_iterations` to prevent infinite execution.

Architecture:
               [START]
                  │
        [generate_or_refine] <─────────────┐ (retry with critique)
                  │                        │
         [evaluate_candidate]              │
                  │                        │
         (check_evaluation)                │
         ├── if failed & iter < max ───────┘
         ├── if passed ───────────> [finalize_solution] ─────> [END]
         └── if failed & iter >= max ─> [fallback_escalation] ─> [END]
"""

import ast
import traceback
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

from statecraft.state import SelfCorrectionState, CodeFeedback
from statecraft.llm import get_llm, extract_code_block


def generate_or_refine(state: SelfCorrectionState) -> Dict[str, Any]:
    """Node: Generates initial code or refines previous code using evaluator critique."""
    task = state.get("task", "")
    iteration = state.get("iterations", 0) + 1
    feedback = state.get("feedback")
    llm = get_llm()

    if feedback and not feedback.get("passed", False):
        # Refinement prompt incorporating error feedback
        errors_str = "\n".join(feedback.get("errors", []))
        critique_str = feedback.get("critique", "")
        prompt = (
            f"Solve this coding task: {task}\n\n"
            f"Previous code had errors:\n{errors_str}\n"
            f"Critique: {critique_str}\n"
            f"Fix the following code and return the corrected Python implementation."
        )
    else:
        # Initial generation prompt
        prompt = f"Generate Python code to solve this coding task: {task}"

    raw_response = llm.invoke(prompt)
    clean_code = extract_code_block(raw_response, "python")

    return {
        "code": clean_code,
        "iterations": iteration,
        "logs": [f"[Cycle {iteration}] Synthesized candidate code ({len(clean_code)} chars)."]
    }


def evaluate_candidate(state: SelfCorrectionState) -> Dict[str, Any]:
    """Node: Executes syntax validation and runs the test suite against the candidate."""
    code = state.get("code", "")
    iteration = state.get("iterations", 1)
    errors: list[str] = []
    syntax_valid = False
    tests_passed = 0
    total_tests = 3
    critique = ""

    # 1. Syntax AST validation
    try:
        ast.parse(code)
        syntax_valid = True
    except SyntaxError as se:
        errors.append(f"SyntaxError on line {se.lineno}: {se.msg}")
        critique = f"Code has invalid Python syntax: {se.msg}"

    # 2. Functional execution validation in sandbox namespace
    if syntax_valid:
        sandbox_scope: Dict[str, Any] = {}
        try:
            exec(code, sandbox_scope)
            
            # Run test cases against calculate_moving_average
            fn = sandbox_scope.get("calculate_moving_average")
            if not callable(fn):
                errors.append("Function 'calculate_moving_average' not defined.")
                critique = "Expected function calculate_moving_average was not found in namespace."
            else:
                # Test 1: Standard window
                res1 = fn([10, 20, 30, 40], 2)
                if res1 == [15.0, 25.0, 35.0]:
                    tests_passed += 1
                else:
                    errors.append(f"Test 1 failed: expected [15.0, 25.0, 35.0], got {res1}")

                # Test 2: Window equals length
                res2 = fn([5, 15], 2)
                if res2 == [10.0]:
                    tests_passed += 1
                else:
                    errors.append(f"Test 2 failed: expected [10.0], got {res2}")

                # Test 3: Empty input boundary check
                res3 = fn([], 2)
                if res3 == []:
                    tests_passed += 1
                else:
                    errors.append(f"Test 3 failed: expected [], got {res3}")

                if tests_passed == total_tests:
                    critique = "All unit tests and boundary assertions passed successfully."
                else:
                    critique = f"Passed {tests_passed}/{total_tests} tests. Fix boundary edge cases and loop bounds."

        except Exception as exc:
            tb = traceback.format_exc(limit=2)
            errors.append(f"Runtime Exception: {exc}\n{tb}")
            critique = f"Execution crashed with error: {exc}"

    all_passed = (syntax_valid and tests_passed == total_tests)
    feedback: CodeFeedback = {
        "passed": all_passed,
        "syntax_valid": syntax_valid,
        "tests_passed": tests_passed,
        "total_tests": total_tests,
        "errors": errors,
        "critique": critique
    }

    log_entry = (
        f"[Cycle {iteration}] Evaluation: {'PASSED' if all_passed else 'FAILED'} "
        f"({tests_passed}/{total_tests} tests passed). Critique: {critique}"
    )

    return {
        "feedback": feedback,
        "feedback_history": [feedback],
        "is_success": all_passed,
        "logs": [log_entry]
    }


def check_evaluation(state: SelfCorrectionState) -> Literal["generate_or_refine", "finalize_solution", "fallback_escalation"]:
    """Conditional Edge: Decides whether to self-correct, complete, or fail safe."""
    feedback = state.get("feedback")
    iteration = state.get("iterations", 1)
    max_iter = state.get("max_iterations", 3)

    if feedback and feedback.get("passed", False):
        return "finalize_solution"
    elif iteration < max_iter:
        return "generate_or_refine"
    else:
        return "fallback_escalation"


def finalize_solution(state: SelfCorrectionState) -> Dict[str, Any]:
    """Node: Formats final verified artifact."""
    iterations = state.get("iterations", 1)
    return {
        "status": "SUCCESS",
        "logs": [f"[Completed] Verified solution achieved in {iterations} iteration(s). Ready for deployment."]
    }


def fallback_escalation(state: SelfCorrectionState) -> Dict[str, Any]:
    """Node: Graceful degradation when max retry limit is exceeded."""
    iterations = state.get("iterations", 1)
    return {
        "status": "ESCALATED_TO_HUMAN",
        "logs": [f"[Escalation] Exceeded max iterations ({iterations}). Bounded fallback triggered safely."]
    }


def build_self_correction_graph(checkpointer: Any = None):
    """Compiles and returns the Self-Correction StateGraph."""
    graph = StateGraph(SelfCorrectionState)

    # 1. Add nodes
    graph.add_node("generate_or_refine", generate_or_refine)
    graph.add_node("evaluate_candidate", evaluate_candidate)
    graph.add_node("finalize_solution", finalize_solution)
    graph.add_node("fallback_escalation", fallback_escalation)

    # 2. Add edges
    graph.add_edge(START, "generate_or_refine")
    graph.add_edge("generate_or_refine", "evaluate_candidate")

    # 3. Add conditional loop edge
    graph.add_conditional_edges(
        "evaluate_candidate",
        check_evaluation,
        {
            "generate_or_refine": "generate_or_refine",
            "finalize_solution": "finalize_solution",
            "fallback_escalation": "fallback_escalation",
        }
    )

    graph.add_edge("finalize_solution", END)
    graph.add_edge("fallback_escalation", END)

    return graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    app = build_self_correction_graph()
    initial_state = {
        "task": "Write calculate_moving_average(numbers: list[float], window_size: int) -> list[float]",
        "max_iterations": 3,
        "iterations": 0,
        "logs": []
    }
    print("="*60)
    print("Running Self-Correction & Evaluator-Optimizer Graph...")
    result = app.invoke(initial_state)
    print(f"\nFinal Status: {result['status']}")
    print(f"Total Iterations: {result['iterations']}")
    print("\nExecution Logs:")
    for log in result.get("logs", []):
        print(f"  {log}")
    print("\nFinal Verified Code:\n" + result["code"])
