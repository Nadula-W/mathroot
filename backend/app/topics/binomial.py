"""First complete topic: Grade 10 binomial expressions / expanding brackets.

This initial generator is symbolic (not an LLM). It creates fresh numerical
variants, verifies the options with SymPy, and attaches diagnostic distractors.
"""
import random
from uuid import uuid4
from sympy import Symbol, expand, simplify

from app.contracts import InternalQuestion, InternalOption

x = Symbol('x')


def _as_text(coefficient: int, constant: int) -> str:
    """Format `coefficient*x + constant` as friendly algebra."""
    if coefficient == 0:
        x_part = ''
    elif coefficient == 1:
        x_part = 'x'
    elif coefficient == -1:
        x_part = '-x'
    else:
        x_part = f'{coefficient}x'
    if constant == 0:
        return x_part or '0'
    if not x_part:
        return str(constant)
    sign = '+' if constant > 0 else '-'
    return f'{x_part} {sign} {abs(constant)}'


class BinomialTopic:
    topic_id = 'binomial'
    title = 'Grade 10 — Binomial Expressions'

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.SystemRandom()

    def generate_question(self, difficulty: str) -> InternalQuestion:
        if difficulty not in {'easy', 'medium', 'hard'}:
            raise ValueError('Difficulty must be easy, medium, or hard.')
        if difficulty == 'easy':
            a = self.rng.randint(2, 6)
            b = self.rng.randint(2, 9)
        elif difficulty == 'medium':
            a = self.rng.randint(2, 7)
            b = -self.rng.randint(2, 9)
        else:
            a = -self.rng.randint(2, 7)
            b = self.rng.choice([-1, 1]) * self.rng.randint(2, 9)

        statement = f"Expand and simplify: {a}({('x + ' + str(b)) if b >= 0 else ('x - ' + str(abs(b)))})"
        expected = expand(a * (x + b))

        # Each incorrect option is deliberately connected to a meaningful error.
        raw_options = [
            ('correct', a * x + a * b, None),
            ('wrong_constant', a * x + b, 'DISTRIBUTION_CONSTANT'),
            ('wrong_variable', x + a * b, 'DISTRIBUTION_VARIABLE'),
            ('wrong_sign', a * x - a * b, 'SIGN_ERROR'),
        ]
        # Recalculate equivalence with SymPy rather than trusting the LLM or templates.
        for idx, (_, expression, _) in enumerate(raw_options):
            if (simplify(expression - expected) == 0) != (idx == 0):
                raise ValueError('Generated an invalid distractor or answer.')
            for other_idx in range(idx):
                if simplify(expression - raw_options[other_idx][1]) == 0:
                    raise ValueError('Generated duplicate answer options.')

        # Opaque IDs prevent student clients from reading answer semantics.
        correct_option_id = str(uuid4())
        identified = [
            (correct_option_id if label is None else str(uuid4()), expr, label)
            for _, expr, label in raw_options
        ]
        self.rng.shuffle(identified)
        options = [
            InternalOption(id=option_id, text=_as_text(int(expr.coeff(x)), int(expr.subs(x, 0))), misconception=label)
            for option_id, expr, label in identified
        ]
        answer_text = _as_text(a, a * b)
        explanation = f'Distribute {a} to BOTH terms: {a} × x = {_as_text(a, 0)} and {a} × ({b}) = {a * b}. The answer is {answer_text}.'
        return InternalQuestion(
            id=str(uuid4()), topic_id=self.topic_id, difficulty=difficulty,
            statement=statement, options=options,
            correct_option_id=correct_option_id, explanation=explanation,
            source_expression=f'{a}*(x+({b}))', correct_expression=str(expected),
        )

    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        if misconception is None:
            return 'Correct. You distributed multiplication to both terms. ' + question.explanation
        messages = {
            'DISTRIBUTION_CONSTANT': 'You may have multiplied the x term but forgotten to multiply the constant. ',
            'DISTRIBUTION_VARIABLE': 'You may have multiplied the constant but forgotten to multiply the x term. ',
            'SIGN_ERROR': 'You may have changed a sign when multiplying the constant. Review multiplication with negative numbers. ',
        }
        return messages.get(misconception, 'Review the distributive law. ') + question.explanation

    def teaching_recommendation(self, misconception: str) -> str:
        recommendations = {
            'DISTRIBUTION_CONSTANT': 'Demonstrate how the outside coefficient multiplies BOTH bracket terms, then assign two expansion examples.',
            'DISTRIBUTION_VARIABLE': 'Review multiplication of coefficients and variables before expanding brackets.',
            'SIGN_ERROR': 'Revisit signed-number multiplication, then practise bracket expansion with negative constants.',
        }
        return recommendations.get(misconception, 'Review expansion of brackets with another worked example.')
