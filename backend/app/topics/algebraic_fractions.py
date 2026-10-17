"""Placeholder for Grade 10 — Algebraic Fractions. Owned by its assigned group member.

Follow the interface in app/topics/base.py and register when complete.
"""
from app.contracts import InternalQuestion


class AlgebraicFractionsTopic:
    topic_id = 'algebraic_fractions'
    title = 'Grade 10 — Algebraic Fractions'

    def generate_question(self, difficulty: str) -> InternalQuestion:
        raise NotImplementedError('Implement and validate this topic generator.')

    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        raise NotImplementedError('Implement student feedback for this topic.')

    def teaching_recommendation(self, misconception: str) -> str:
        raise NotImplementedError('Implement teacher feedback for this topic.')
