"""Placeholder for Grade 10 — Equations. Owned by its assigned group member.

Follow the interface in app/topics/base.py and register when complete.
"""
from app.contracts import InternalQuestion


class EquationsTopic:
    topic_id = 'equations'
    title = 'Grade 10 — Equations'

    def generate_question(self, difficulty: str) -> InternalQuestion:
        raise NotImplementedError('Implement and validate this topic generator.')

    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        raise NotImplementedError('Implement student feedback for this topic.')

    def teaching_recommendation(self, misconception: str) -> str:
        raise NotImplementedError('Implement teacher feedback for this topic.')
