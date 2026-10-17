"""Placeholder for Grade 10 — Factors of Quadratic Expressions. Owned by its assigned group member.

Follow the interface in app/topics/base.py and register when complete.
"""
from app.contracts import InternalQuestion


class FactorizationTopic:
    topic_id = 'factorization'
    title = 'Grade 10 — Factors of Quadratic Expressions'

    def generate_question(self, difficulty: str) -> InternalQuestion:
        raise NotImplementedError('Implement and validate this topic generator.')

    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        raise NotImplementedError('Implement student feedback for this topic.')

    def teaching_recommendation(self, misconception: str) -> str:
        raise NotImplementedError('Implement teacher feedback for this topic.')
