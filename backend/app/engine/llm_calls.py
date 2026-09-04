import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import anthropic

from app.config import settings
from app.graph.loader import graph_store
from app.models.schemas import (
    ConceptNode,
    ProbingQuestionResult,
    GapClassificationResult,
    TeachBackGradingResult,
)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt_template(filename: str) -> str:
    template_path = PROMPTS_DIR / filename
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


class LLMDiagnosticService:
    """
    Orchestrates grounded Claude API calls using forced tool-use / structured JSON outputs.
    Falls back gracefully to deterministic pedagogical mocks when in offline/mock mode.
    """

    @staticmethod
    async def generate_probing_question(node: ConceptNode) -> ProbingQuestionResult:
        """Task 1: Generate 1 targeted question grounded in candidate node description & mastery signal."""
        # Validate node exists in graph (Rule §2)
        if not graph_store.get_node(node.id):
            raise ValueError(f"Unknown concept node: {node.id}")

        # Deterministic Mock Mode
        if settings.MOCK_LLM or not settings.ANTHROPIC_API_KEY:
            mock_questions = {
                "base_case": "In a recursive function, what exact role does the base case play, and what happens if it is omitted?",
                "recursive_step": "How does the recursive step ensure the problem gets smaller rather than repeating indefinitely?",
                "call_stack": "When a function calls another function, what happens to the variables of the first function in memory?",
                "functions": "What is the difference between defining a function with def and calling/invoking it?",
                "conditionals": "If you have an if/elif/else structure, under what circumstances will more than one branch execute?",
                "comparison_operators": "What is the operational difference between the '=' operator and the '==' operator in Python?",
                "return_values": "What is the difference between printing a calculation result and returning it from a function?",
            }
            q = mock_questions.get(
                node.id,
                f"How would you explain the core mechanism of {node.name} ({node.description})?"
            )
            return ProbingQuestionResult(concept_id=node.id, question=q, is_mock=True)

        # Live Claude Structured Tool Call
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        template = _load_prompt_template("probing_question.md")
        prompt = template.format(
            concept_name=node.name,
            concept_description=node.description,
            concept_mastery_signal=node.mastery_signal,
        )

        tool_schema = {
            "name": "generate_probing_question",
            "description": "Returns a focused diagnostic probing question.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The probing question"},
                    "concept_id": {"type": "string", "description": "The concept ID being probed"}
                },
                "required": ["question", "concept_id"]
            }
        }

        response = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=256,
            tools=[tool_schema],
            tool_choice={"type": "tool", "name": "generate_probing_question"},
            messages=[{"role": "user", "content": prompt}],
        )

        tool_block = next((b for b in response.content if b.type == "tool_use"), None)
        if not tool_block:
            raise RuntimeError("Claude did not return expected tool_use block for probing question")

        data = tool_block.input
        return ProbingQuestionResult(
            concept_id=node.id,
            question=data.get("question", f"Explain how {node.name} works."),
            is_mock=False,
        )

    @staticmethod
    async def classify_gap(
        node: ConceptNode,
        question: str,
        student_answer: str,
    ) -> GapClassificationResult:
        """Task 2: Classify whether student's answer reveals a gap, grounded against stored mastery_signal."""
        if not graph_store.get_node(node.id):
            raise ValueError(f"Unknown concept node: {node.id}")

        # Deterministic Mock Mode
        if settings.MOCK_LLM or not settings.ANTHROPIC_API_KEY:
            lower = student_answer.lower()
            # If answer is vague, wrong, or expresses confusion -> gap detected
            gap_keywords = ["not sure", "don't know", "idk", "repeats", "forever", "nothing", "loops", "runs forever", "error"]
            has_gap_phrase = any(k in lower for k in gap_keywords) or len(student_answer.strip()) < 15

            # On the scripted demo path, answering about conditionals or base case confusion triggers the gap:
            is_gap = has_gap_phrase or ("base" not in lower and node.id in ["base_case", "conditionals"])

            reason = (
                f"Student answer reflects confusion regarding {node.name} and fails to meet the mastery signal: '{node.mastery_signal}'."
                if is_gap
                else f"Student answer adequately demonstrates understanding of {node.name}, satisfying: '{node.mastery_signal}'."
            )
            return GapClassificationResult(
                concept_id=node.id,
                gap_detected=is_gap,
                confidence=0.88,
                reasoning=reason,
                is_mock=True,
            )

        # Live Claude Structured Tool Call
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        template = _load_prompt_template("gap_classification.md")
        prompt = template.format(
            concept_name=node.name,
            concept_description=node.description,
            concept_mastery_signal=node.mastery_signal,
            question=question,
            student_answer=student_answer,
        )

        tool_schema = {
            "name": "classify_gap",
            "description": "Classify whether student exhibits a gap based on mastery signal.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "gap_detected": {"type": "boolean", "description": "True if student has a gap"},
                    "confidence": {"type": "number", "description": "Confidence score 0.0 to 1.0"},
                    "reasoning": {"type": "string", "description": "Pedagogical justification"}
                },
                "required": ["gap_detected", "confidence", "reasoning"]
            }
        }

        response = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=256,
            tools=[tool_schema],
            tool_choice={"type": "tool", "name": "classify_gap"},
            messages=[{"role": "user", "content": prompt}],
        )

        tool_block = next((b for b in response.content if b.type == "tool_use"), None)
        if not tool_block:
            raise RuntimeError("Claude did not return expected tool_use block for gap classification")

        data = tool_block.input
        return GapClassificationResult(
            concept_id=node.id,
            gap_detected=bool(data["gap_detected"]),
            confidence=float(data.get("confidence", 0.85)),
            reasoning=str(data.get("reasoning", "")),
            is_mock=False,
        )

    @staticmethod
    async def grade_teach_back(
        node: ConceptNode,
        student_explanation: str,
    ) -> TeachBackGradingResult:
        """Task 3: Grade student's own-words teach-back against the node's stored teach_back_rubric."""
        if not graph_store.get_node(node.id):
            raise ValueError(f"Unknown concept node: {node.id}")

        # Deterministic Mock Mode
        if settings.MOCK_LLM or not settings.ANTHROPIC_API_KEY:
            # Check length and presence of explanatory words
            is_meaningful = len(student_explanation.strip()) >= 25
            met_points = node.teach_back_rubric if is_meaningful else node.teach_back_rubric[:1]

            feedback = (
                f"Great explanation of {node.name}! You correctly highlighted the key principles: "
                + "; ".join(met_points)
                + ". You're ready to retry the problem!"
                if is_meaningful
                else f"Your explanation is a bit too brief. Please explain more specifically: {'; '.join(node.teach_back_rubric)}."
            )

            return TeachBackGradingResult(
                concept_id=node.id,
                understood=is_meaningful,
                feedback=feedback,
                rubric_points_met=met_points,
                is_mock=True,
            )

        # Live Claude Structured Tool Call
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        template = _load_prompt_template("teach_back_grading.md")
        rubric_formatted = "\n".join(f"- {pt}" for pt in node.teach_back_rubric)
        prompt = template.format(
            concept_name=node.name,
            concept_description=node.description,
            rubric_points=rubric_formatted,
            student_explanation=student_explanation,
        )

        tool_schema = {
            "name": "grade_teach_back",
            "description": "Grades student teach-back explanation against rubric.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "understood": {"type": "boolean", "description": "True if student demonstrated understanding"},
                    "feedback": {"type": "string", "description": "Constructive feedback"},
                    "rubric_points_met": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Rubric criteria points that were satisfied"
                    }
                },
                "required": ["understood", "feedback", "rubric_points_met"]
            }
        }

        response = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=384,
            tools=[tool_schema],
            tool_choice={"type": "tool", "name": "grade_teach_back"},
            messages=[{"role": "user", "content": prompt}],
        )

        tool_block = next((b for b in response.content if b.type == "tool_use"), None)
        if not tool_block:
            raise RuntimeError("Claude did not return expected tool_use block for teach-back grading")

        data = tool_block.input
        return TeachBackGradingResult(
            concept_id=node.id,
            understood=bool(data["understood"]),
            feedback=str(data.get("feedback", "")),
            rubric_points_met=list(data.get("rubric_points_met", [])),
            is_mock=False,
        )
