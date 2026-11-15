"""Nimsara: AI-first question generation and the existing TopicModule adapter.

Provider failures fall back to independently validated manual mathematics.
"""
from app.contracts import InternalQuestion
from . import ai, manual, presentation


def generate_question(difficulty: str) -> InternalQuestion:
    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("Difficulty must be easy, medium, or hard.")
    # The topic's mode is independent of Nadula's question-generation settings.
    if ai.configuration()["mode"] == "manual":
        question = manual.generate_question(difficulty)
    else:
        try:
            question = ai.generate_question(difficulty)
            if question.difficulty != difficulty:
                raise ValueError("Provider returned the wrong difficulty.")
            # Never trust a provider's answer key without deterministic checking.
            manual.validate_question(question)
            return question
        except Exception:
            # Missing provider/model, timeout, bad schema or invalid mathematics.
            # Do not log API keys, prompts, provider bodies or student information.
            question = manual.generate_question(difficulty)
    manual.validate_question(question)
    return question


class EquationsTopic:
    topic_id = "equations"
    title = "Equations"
    misconception_definitions = manual.MISCONCEPTIONS

    def generate_question(self, difficulty: str) -> InternalQuestion:
        return generate_question(difficulty)

    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        return manual.feedback(question, misconception)

    def teaching_recommendation(self, misconception: str) -> str:
        return manual.teaching_recommendation(misconception)

    def answer_feedback_provider(self):
        # The shared verifier calls this optional hook after registration.
        return ai.TopicFeedbackProvider()


    def presentation_text(self, field: str, text: str, question=None, misconception=None):
        return presentation.presentation_text(field, text, question, misconception)

    def translation_provider(self):
        # Optional: use this topic's own provider, never Nadula's configuration.
        return ai.TopicTranslationProvider()

    def validate_translation(self, field: str, source: str, translated: str, question=None) -> bool:
        return presentation.validate_translation(field, source, translated, question)
