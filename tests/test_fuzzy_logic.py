import pytest

from src.models.ml_algorithms import FuzzyLogicEngine


@pytest.fixture
def engine():
    return FuzzyLogicEngine({})


def test_triangular_membership(engine):
    params = (0.0, 0.5, 1.0)
    assert engine.triangular_membership(-0.1, params) == 0.0
    assert engine.triangular_membership(0.0, params) == 0.0
    assert engine.triangular_membership(0.25, params) == pytest.approx(0.5)
    assert engine.triangular_membership(0.5, params) == 1.0
    assert engine.triangular_membership(0.75, params) == pytest.approx(0.5)
    assert engine.triangular_membership(1.0, params) == 0.0
    assert engine.triangular_membership(1.5, params) == 0.0


def test_make_decision(engine):
    result = engine.make_decision({"task_complexity": 0.2, "agent_workload": 0.2})
    assert result == {"decision": {"assignment_score": 0.9}, "confidence": 0.8}

    result = engine.make_decision({"task_complexity": 0.8, "agent_workload": 0.2})
    assert result["decision"]["assignment_score"] == 0.2
    assert result["confidence"] == 0.8

    result = engine.make_decision({"task_complexity": 0.5, "agent_workload": 0.5})
    assert result["decision"]["assignment_score"] == 0.5
    assert result["confidence"] == 0.8
