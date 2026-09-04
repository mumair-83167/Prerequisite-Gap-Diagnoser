import pytest
from app.graph.loader import graph_store
from app.engine.llm_calls import LLMDiagnosticService
from app.models.schemas import (
    ProbingQuestionResult,
    GapClassificationResult,
    TeachBackGradingResult,
)


@pytest.mark.anyio
async def test_generate_probing_question():
    """Verify probing question generator returns a grounded question."""
    node = graph_store.get_node("conditionals")
    assert node is not None

    res = await LLMDiagnosticService.generate_probing_question(node)
    assert isinstance(res, ProbingQuestionResult)
    assert res.concept_id == "conditionals"
    assert len(res.question.strip()) > 10


@pytest.mark.anyio
async def test_classify_gap_with_gap():
    """Verify gap classification detects a misconception/confusion."""
    node = graph_store.get_node("conditionals")
    assert node is not None

    question = "Under what conditions will more than one branch execute?"
    answer = "I don't know, it keeps running all of them forever"

    res = await LLMDiagnosticService.classify_gap(node, question, answer)
    assert isinstance(res, GapClassificationResult)
    assert res.concept_id == "conditionals"
    assert res.gap_detected is True
    assert 0.0 <= res.confidence <= 1.0
    assert len(res.reasoning) > 10


@pytest.mark.anyio
async def test_classify_gap_with_mastery():
    """Verify gap classification recognizes when student meets the mastery signal."""
    node = graph_store.get_node("functions")
    assert node is not None

    question = "What is the difference between defining and calling a function?"
    answer = "Defining creates the function using def, but calling it executes the code inside."

    res = await LLMDiagnosticService.classify_gap(node, question, answer)
    assert isinstance(res, GapClassificationResult)
    assert res.concept_id == "functions"
    assert res.gap_detected is False


@pytest.mark.anyio
async def test_grade_teach_back():
    """Verify teach-back grading properly evaluates own-words explanation."""
    node = graph_store.get_node("conditionals")
    assert node is not None

    # Comprehensive explanation
    good_explanation = (
        "An if statement evaluates a boolean condition. If it is True, only that block runs. "
        "The elif checks other mutually exclusive branches, and else is the catch-all when everything is False."
    )
    res_good = await LLMDiagnosticService.grade_teach_back(node, good_explanation)
    assert isinstance(res_good, TeachBackGradingResult)
    assert res_good.understood is True
    assert len(res_good.rubric_points_met) >= 1

    # Incomplete explanation
    brief_explanation = "it checks things"
    res_bad = await LLMDiagnosticService.grade_teach_back(node, brief_explanation)
    assert isinstance(res_bad, TeachBackGradingResult)
    assert res_bad.understood is False
