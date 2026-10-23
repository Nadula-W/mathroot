"""Nimsara: deterministic mathematics and fallback. No completed math is supplied."""
from app.contracts import InternalQuestion


def generate_question(difficulty: str) -> InternalQuestion:
    # TODO: Generate an original syllabus-aligned question for this difficulty.
    # Return InternalQuestion with opaque UUIDs, four distinct InternalOption
    # values, one correct_option_id, explanation, source_expression and
    # correct_expression. Label diagnostic distractors with stable codes.
    raise NotImplementedError("Implement equations manual question generation.")


def validate_question(question: InternalQuestion) -> None:
    # TODO: Independently verify the key and every distractor using appropriate
    # deterministic mathematics/SymPy. Reject duplicates and invalid questions.
    # Check domain restrictions (e.g. nonzero denominators) where relevant.
    # Never eval, parse_expr or sympify untrusted provider/student strings.
    raise NotImplementedError("Implement equations mathematical validation.")


def verify_answer(question: InternalQuestion, option_id: str) -> bool:
    """Deterministic MCQ verification against a mathematically validated key."""
    validate_question(question)
    if option_id not in {option.id for option in question.options}:
        raise ValueError("Unknown answer option.")
    return option_id == question.correct_option_id


def feedback(question: InternalQuestion, misconception: str | None) -> str:
    # TODO: Return trusted worked steps and a possible-misconception explanation.
    # None is used for correct selections; unknown wrong selections are handled
    # by the shared verifier. Never diagnose a misconception as proven.
    raise NotImplementedError("Implement equations manual feedback.")


def teaching_recommendation(misconception: str) -> str:
    # TODO: Map your stable codes to specific correction/practice activities.
    # Include a safe generic recommendation for unknown codes.
    raise NotImplementedError("Implement equations teaching recommendations.")
