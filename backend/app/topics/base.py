#Rules that all five members must followRules that all five members must follow
from typing import Protocol
from app.contracts import InternalQuestion


class TopicModule(Protocol):
    """Required mathematics contract; bilingual presentation remains optional.

    Completed topics may also expose presentation_text(field, text,
    question=None, misconception=None) for reviewed Sinhala templates, and
    translation_provider()/validate_translation(field, source, translated,
    question=None) for optional AI translation. These are display hooks only;
    the shared presentation service keeps canonical mathematics unchanged.
    """
    topic_id: str
    title: str

    def generate_question(self, difficulty: str) -> InternalQuestion:
        """Create an original, mathematically verified question."""
        ...

    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        """Generate a concept-specific explanation after an answer."""
        ...

    def teaching_recommendation(self, misconception: str) -> str:
        """A concrete next-class correction activity."""
        ...
