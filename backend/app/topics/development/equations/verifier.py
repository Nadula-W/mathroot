"""Nimsara: independent topic checks using the existing shared verifier."""
from app.answer_verification import verify_answer as shared_verify_answer
from app.contracts import InternalQuestion
from . import manual
from .generator import EquationsTopic


def verify_answer(question: InternalQuestion, option_id: str) -> dict:
    # Independently validate generated mathematics and the submitted option.
    # No AI opinion can change this deterministic key check.
    manual.verify_answer(question, option_id)
    # Reuse shared grading, output validation, confidence checks and automatic
    # fallback; this topic's optional provider hook selects its own provider.
    return shared_verify_answer(question, option_id, EquationsTopic())


# TODO: Define diagnostic codes in EquationsTopic.misconception_definitions,
# attach them to evidence-bearing distractors in your generators, and implement
# feedback/teaching actions in manual.py. Do not invent diagnoses from no evidence.
# For future free-text input, use a bounded safe mathematical parser and explicit
# domain rules. Keep current MCQ request/response contracts unchanged.
