"""Fernando: AI-first question generation and the existing TopicModule adapter.

Unfinished: do not register this topic until manual and AI paths are validated.
"""
from app.contracts import InternalQuestion
from . import ai, manual


def generate_question(difficulty: str) -> InternalQuestion:
    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("Difficulty must be easy, medium, or hard.")
    # The topic's mode is independent of Nadula's question-generation settings.
    if ai.configuration()["mode"] == "manual":
        question = manual.generate_question(difficulty)
    else:
        try:
            question = ai.generate_question(difficulty)
            # Never trust a provider's answer key without deterministic checking.
            manual.validate_question(question)
            return question
        except Exception:
            # Missing provider/model, timeout, bad schema or invalid mathematics.
            # Do not log API keys, prompts, provider bodies or student information.
            question = manual.generate_question(difficulty)
    manual.validate_question(question)
    return question


def generate_remediation_question(
    difficulty: str,
    exclude_params: set[tuple] | None = None,
) -> InternalQuestion:
    """Generate an unseen remediation question variation from the same family.

    AI parameter selection is attempted when configured, strictly validated against
    the exclusion set, and falls back to deterministic manual variations if AI fails
    or produces previously used parameters.
    """
    exclude = set(exclude_params or ())
    if ai.configuration()["mode"] == "manual":
        return manual.generate_remediation_variation(difficulty, exclude_params=exclude)
    try:
        question = ai.generate_remediation_question(difficulty, exclude_params=exclude)
        manual.validate_question(question)
        return question
    except Exception:
        question = manual.generate_remediation_variation(difficulty, exclude_params=exclude)
    manual.validate_question(question)
    return question


class AlgebraicFractionsTopic:
    topic_id = "algebraic_fractions"
    title = "Algebraic Fractions"
    # TODO: Populate with stable codes supported by your diagnostic distractors.
    misconception_definitions: dict[str, str] = {
        "DENOMINATOR_ADDITION": "Added denominators directly across fractions instead of finding or keeping a common denominator.",
        "UNSCALED_NUMERATOR": "Converted to a common denominator but failed to scale the numerator by the corresponding factor.",
        "SIGN_ERROR": "Added numerators instead of subtracting (or subtracted instead of adding).",
        "SIGN_DISTRIBUTION_ERROR": "Failed to distribute the negative sign across both terms of a binomial numerator during subtraction.",
        "NUMERATOR_OPERATION_CONFUSION": "Multiplied numerators instead of adding or subtracting them.",
    }

    def generate_question(self, difficulty: str) -> InternalQuestion:
        return generate_question(difficulty)

    def generate_remediation_question(
        self, difficulty: str, exclude_params: set[tuple] | None = None
    ) -> InternalQuestion:
        return generate_remediation_question(difficulty, exclude_params=exclude_params)

    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        return manual.feedback(question, misconception)

    def teaching_recommendation(self, misconception: str) -> str:
        return manual.teaching_recommendation(misconception)

    def answer_feedback_provider(self):
        # The shared verifier calls this optional hook after registration.
        return ai.TopicFeedbackProvider()

    def presentation_text(self, field: str, text: str, question=None, misconception=None):
        from .presentation import presentation_text
        return presentation_text(field, text, question=question, misconception=misconception)

    def translation_provider(self):
        # Dynamic AI translation is unfinished; return None to avoid exposing an incomplete provider.
        return None

    def validate_translation(self, field: str, source: str, translated: str, question=None) -> bool:
        expected = self.presentation_text(field, source, question=question)
        return expected is not None and expected == translated
