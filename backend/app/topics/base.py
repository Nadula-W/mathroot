"""Interface specification. Other team members can implement TopicModule."""
from typing import Protocol
from app.contracts import InternalQuestion


class TopicModule(Protocol):
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
