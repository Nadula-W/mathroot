"""Deterministic linear equations with exact rational arithmetic."""
from fractions import Fraction
import random
import re
from uuid import uuid4
from app.contracts import InternalQuestion, InternalOption

MISCONCEPTIONS = {
    'INVERSE_SIGN': 'Added the constant instead of subtracting it.',
    'MISSING_DIVISION': 'Stopped before dividing by the coefficient.',
    'NEGATED_SOLUTION': 'Changed the sign of the solution.',
}
GUIDANCE = {
    'INVERSE_SIGN': 'Undo addition by subtracting the same constant from both sides.',
    'MISSING_DIVISION': 'Divide both sides by the remaining variable coefficient.',
    'NEGATED_SOLUTION': 'Practise signed division and check by substitution.',
}
N = r'(-?\d{1,4})'
PATTERNS = {
    'easy': re.compile(rf'{N}\*x \+ \({N}\) = {N}'),
    'medium': re.compile(rf'{N}\*x \+ \({N}\) = {N}\*x \+ \({N}\)'),
    'hard': re.compile(rf'{N}\*\(x \+ \({N}\)\) = {N}\*x \+ \({N}\)'),
}


def _derive(difficulty, source):
    pattern = PATTERNS.get(difficulty)
    match = pattern.fullmatch(source) if pattern and len(source) <= 100 else None
    if not match:
        raise ValueError('Unsupported equation format.')
    values = tuple(map(int, match.groups()))
    if difficulty == 'easy':
        a, b, d = values
        c = 0
    else:
        a, b, c, d = values
        if difficulty == 'hard':
            b *= a
    coefficient, constant = a - c, d - b
    if not coefficient:
        raise ValueError('Equation must have exactly one solution.')
    solution = Fraction(constant, coefficient)
    answers = [solution, Fraction(d + b, coefficient), Fraction(constant), -solution]
    if len(set(answers)) != 4:
        raise ValueError('Duplicate diagnostic options.')
    explanation = (
        f'Collect terms: ({a} - ({c}))*x = {d} - ({b}). '
        f'Thus {coefficient}*x = {constant}. Divide both sides by {coefficient}: x = {solution}. '
        f'Substitution gives {a * solution + b} on both sides.'
    )
    return answers, explanation


def generate_question(difficulty: str) -> InternalQuestion:
    if difficulty not in PATTERNS:
        raise ValueError('Difficulty must be easy, medium, or hard.')
    rng = random.SystemRandom()
    for _ in range(300):
        a = rng.randint(2, 12) * (rng.choice([-1, 1]) if difficulty == 'hard' else 1)
        b = rng.randint(1, 15) * (1 if difficulty == 'easy' else rng.choice([-1, 1]))
        c = 0 if difficulty == 'easy' else rng.randint(1, 9)
        solution = Fraction(rng.choice([i for i in range(-15, 16) if i]), rng.randint(2, 5) if difficulty == 'hard' else 1)
        d = (a - c) * solution + (a * b if difficulty == 'hard' else b)
        if d.denominator != 1:
            continue
        if difficulty == 'easy':
            source = f'{a}*x + ({b}) = {d}'
        elif difficulty == 'medium':
            source = f'{a}*x + ({b}) = {c}*x + ({d})'
        else:
            source = f'{a}*(x + ({b})) = {c}*x + ({d})'
        try:
            answers, explanation = _derive(difficulty, source)
        except ValueError:
            continue
        return from_source(difficulty, source)
    raise RuntimeError('Could not generate distinct options.')


def from_source(difficulty: str, source: str) -> InternalQuestion:
    """Construct trusted options and working from a bounded equation template."""
    answers, explanation = _derive(difficulty, source)
    options = [InternalOption(str(uuid4()), f'x = {v}', code)
               for v, code in zip(answers, [None, *MISCONCEPTIONS])]
    correct_id = options[0].id
    random.SystemRandom().shuffle(options)
    question = InternalQuestion(str(uuid4()), 'equations', difficulty,
        f'Solve for x: {source}', options, correct_id, explanation, source, str(answers[0]))
    validate_question(question)
    return question


def validate_question(question: InternalQuestion) -> None:
    answers, explanation = _derive(question.difficulty, question.source_expression)
    if (question.topic_id != 'equations' or not question.id
            or question.statement != f'Solve for x: {question.source_expression}'
            or question.explanation != explanation or question.correct_expression != str(answers[0])
            or len(question.options) != 4 or len({o.id for o in question.options}) != 4
            or any(not o.id for o in question.options)):
        raise ValueError('Invalid question metadata.')
    expected = dict(zip([None, *MISCONCEPTIONS], [f'x = {v}' for v in answers]))
    if {o.misconception for o in question.options} != set(expected):
        raise ValueError('Invalid diagnostic labels.')
    for option in question.options:
        if (option.text != expected[option.misconception]
                or (option.id == question.correct_option_id) != (option.misconception is None)):
            raise ValueError('Invalid key or distractor.')


def verify_answer(question: InternalQuestion, option_id: str) -> bool:
    validate_question(question)
    if option_id not in {o.id for o in question.options}:
        raise ValueError('Unknown answer option.')
    return option_id == question.correct_option_id


def feedback(question: InternalQuestion, misconception: str | None) -> str:
    validate_question(question)
    if misconception is None:
        return 'Correct. ' + question.explanation
    evidence = MISCONCEPTIONS.get(misconception)
    return (f'Possible misconception: {evidence} ' if evidence else 'Review your working. ') + question.explanation


def teaching_recommendation(misconception: str) -> str:
    return GUIDANCE.get(misconception, 'Apply the same operation to both sides and check by substitution.')
