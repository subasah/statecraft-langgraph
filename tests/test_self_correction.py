"""Unit tests for Pattern 2: Self-Correction & Evaluator-Optimizer Loop."""

import pytest
from statecraft.patterns.self_correction import build_self_correction_graph


def test_self_correction_recovers_and_passes():
    app = build_self_correction_graph()
    initial_state = {
        "task": "Write calculate_moving_average(numbers: list[float], window_size: int) -> list[float]",
        "max_iterations": 3,
        "iterations": 0,
        "logs": []
    }
    result = app.invoke(initial_state)

    assert result["status"] == "SUCCESS"
    assert result["is_success"] is True
    assert result["iterations"] == 2  # Recovers on attempt 2
    assert len(result["feedback_history"]) == 2
    assert result["feedback_history"][0]["passed"] is False  # Failed cycle 1
    assert result["feedback_history"][1]["passed"] is True   # Passed cycle 2
    assert "def calculate_moving_average" in result["code"]


def test_self_correction_bounds_iteration_limit():
    app = build_self_correction_graph()
    # Provide a task that causes repeated failure with max_iterations=1 to test bounding
    initial_state = {
        "task": "Invalid impossible task syntax",
        "max_iterations": 1,
        "iterations": 0,
        "logs": []
    }
    result = app.invoke(initial_state)
    assert result["iterations"] <= 1
    # Either succeeds or triggers bounded fallback safely
    assert result["status"] in ["SUCCESS", "ESCALATED_TO_HUMAN"]
