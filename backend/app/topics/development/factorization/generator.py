"""Bopage: AI-first question generation and the existing TopicModule adapter.

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


class FactorizationTopic:
    topic_id = "factorization"
    title = "Factors of Quadratic Expressions"
    # TODO: Populate with stable codes supported by your diagnostic distractors.
    misconception_definitions: dict[str, str] = {}

    def generate_question(self, difficulty: str) -> InternalQuestion:
        return generate_question(difficulty)

    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        return manual.feedback(question, misconception)

    def teaching_recommendation(self, misconception: str) -> str:
        return manual.teaching_recommendation(misconception)

    def answer_feedback_provider(self):
        # The shared verifier calls this optional hook after registration.
        return ai.TopicFeedbackProvider()
