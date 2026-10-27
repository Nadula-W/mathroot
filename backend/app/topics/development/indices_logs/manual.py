import random
import re
from typing import NamedTuple
from uuid import uuid4

from sympy import Integer, Rational

from app.contracts import InternalOption, InternalQuestion

TOPIC_ID = "indices_logs"


# ---------- Part 1: question builders (one per law) ----------

class _Draft(NamedTuple):
    statement: str
    source_expression: str
    correct_expression: str
    explanation: str
    options: list  # [(text, value, misconception code)]; first one is correct


def _self_check(options, expected):
    """The builder checks its own work (validate_question checks again later)."""
    values = [value for _, value, _ in options]
    if values[0] != expected:
        raise ValueError("Wrong key.")
    if any(value == expected for value in values[1:]):
        raise ValueError("A distractor equals the correct answer.")
    if len(set(values)) != 4:
        raise ValueError("Duplicate option values.")


def _build_product_law(rng) -> _Draft:
    base = rng.choice([2, 3, 5])
    m = rng.randint(2, 5)
    n = rng.choice([k for k in range(2, 6) if k != m])  # m != n

    options = [
        (f"{base}^{m + n}",        Integer(base) ** (m + n),        None),
        (f"{base}^{m * n}",        Integer(base) ** (m * n),        "MULTIPLIED_EXPONENTS"),
        (f"{base * base}^{m + n}", Integer(base * base) ** (m + n), "MULTIPLIED_BASES"),
        (f"{base}^{abs(m - n)}",   Integer(base) ** abs(m - n),     "SUBTRACTED_EXPONENTS"),
    ]
    _self_check(options, Integer(base) ** m * Integer(base) ** n)
    return _Draft(
        statement=f"Simplify: {base}^{m} × {base}^{n}",
        source_expression=f"{base}^{m}*{base}^{n}",
        correct_expression=f"{base}^{m + n}",
        explanation=(
            f"Same base, so ADD the exponents: {m} + {n} = {m + n}. "
            f"The answer is {base}^{m + n}."
        ),
        options=options,
    )


def _build_quotient_law(rng) -> _Draft:
    base = rng.choice([2, 3, 5, 6])
    n = rng.randint(2, 4)
    # m > n, and m/n is NOT a whole number, so base^(m/n) really looks like a fraction
    m = rng.choice([k for k in range(n + 1, 9) if k % n != 0])

    options = [
        (f"{base}^{m - n}",       Integer(base) ** (m - n),        None),
        (f"{base}^{m + n}",       Integer(base) ** (m + n),        "ADDED_EXPONENTS"),
        (f"{base}^({m}/{n})",     Integer(base) ** Rational(m, n), "DIVIDED_EXPONENTS"),
        (f"1^{m - n}",            Integer(1),                      "DIVIDED_BASES"),
    ]
    _self_check(options, Integer(base) ** m / Integer(base) ** n)
    return _Draft(
        statement=f"Simplify: {base}^{m} ÷ {base}^{n}",
        source_expression=f"{base}^{m}/{base}^{n}",
        correct_expression=f"{base}^{m - n}",
        explanation=(
            f"Same base, so SUBTRACT the exponents: {m} - {n} = {m - n}. "
            f"The answer is {base}^{m - n}."
        ),
        options=options,
    )


_LAWS = {
    "product": _build_product_law,
    "quotient": _build_quotient_law,
}


def _generate_with_retry(builder, rng, tries=20) -> _Draft:
    for _ in range(tries):
        try:
            return builder(rng)
        except ValueError:
            continue
    raise RuntimeError("Could not generate a valid question.")


# ---------- Part 2: required functions ----------

def generate_question(difficulty: str, rng=None, law: str | None = None) -> InternalQuestion:
    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("Difficulty must be easy, medium, or hard.")
    if law is not None and law not in _LAWS:
        raise ValueError(f"Unknown law: {law}")
    rng = rng or random.SystemRandom()

    builder = _LAWS[law] if law else rng.choice(list(_LAWS.values()))
    draft = _generate_with_retry(builder, rng)

    correct_option_id = str(uuid4())
    identified = [
        (correct_option_id if code is None else str(uuid4()), text, code)
        for text, _, code in draft.options
    ]
    rng.shuffle(identified)
    options = [
        InternalOption(id=option_id, text=text, misconception=code)
        for option_id, text, code in identified
    ]
    return InternalQuestion(
        id=str(uuid4()),
        topic_id=TOPIC_ID,
        difficulty=difficulty,
        statement=draft.statement,
        options=options,
        correct_option_id=correct_option_id,
        explanation=draft.explanation,
        source_expression=draft.source_expression,
        correct_expression=draft.correct_expression,
    )


# ---------- Part 3: independent validation ----------

MAX_BASE = 99
MAX_EXPONENT = 50
MAX_ROOT = 10

# "2^7" or "2^(7/2)"
_POWER = re.compile(r"(\d+)\^(?:(\d+)|\((\d+)/(\d+)\))")
_PRODUCT = re.compile(r"(\d+)\^(\d+)\*(\d+)\^(\d+)")
_QUOTIENT = re.compile(r"(\d+)\^(\d+)/(\d+)\^(\d+)")


def _checked_power(base: int, numerator: int, denominator: int = 1):
    """Safe base^(numerator/denominator). Bad or huge numbers are rejected."""
    if not 1 <= base <= MAX_BASE:
        raise ValueError(f"Base {base} is outside the allowed range.")
    if not 0 <= numerator <= MAX_EXPONENT:
        raise ValueError(f"Exponent {numerator} is outside the allowed range.")
    if denominator == 0:
        raise ValueError("A denominator cannot be zero.")
    if not 1 <= denominator <= MAX_ROOT:
        raise ValueError(f"Denominator {denominator} is outside the allowed range.")
    return Integer(base) ** Rational(numerator, denominator)


def _power_value(text: str):
    """Read '2^7' or '2^(7/2)' with a strict pattern (no eval, no sympify)."""
    match = _POWER.fullmatch(text.strip())
    if not match:
        raise ValueError(f"Unreadable power: {text!r}")
    base = int(match[1])
    if match[2] is not None:
        return _checked_power(base, int(match[2]))
    return _checked_power(base, int(match[3]), int(match[4]))


def _expected_value(source_expression: str):
    """Work out the true answer from the source expression."""
    text = source_expression.strip()
    match = _PRODUCT.fullmatch(text)
    if match:
        b1, m, b2, n = (int(g) for g in match.groups())
        return _checked_power(b1, m) * _checked_power(b2, n)
    match = _QUOTIENT.fullmatch(text)
    if match:
        b1, m, b2, n = (int(g) for g in match.groups())
        return _checked_power(b1, m) / _checked_power(b2, n)
    raise ValueError("Unknown question pattern.")


def validate_question(question: InternalQuestion) -> None:
    options = question.options
    ids = [option.id for option in options]

    if len(options) != 4:
        raise ValueError("Exactly 4 options are required.")
    if len(set(ids)) != 4:
        raise ValueError("Option ids must be unique.")
    if question.correct_option_id not in ids:
        raise ValueError("correct_option_id is not one of the options.")

    expected = _expected_value(question.source_expression)
    if _power_value(question.correct_expression) != expected:
        raise ValueError("correct_expression does not match the source expression.")

    values = []
    for option in options:
        value = _power_value(option.text)
        is_key = option.id == question.correct_option_id
        if is_key and option.misconception is not None:
            raise ValueError("The correct option must not have a misconception code.")
        if not is_key and not option.misconception:
            raise ValueError("Every wrong option needs a misconception code.")
        if is_key != (value == expected):
            raise ValueError("Key and distractor values do not match the true answer.")
        values.append(value)

    if len(set(values)) != 4:
        raise ValueError("Duplicate option values.")


def verify_answer(question: InternalQuestion, option_id: str) -> bool:
    """Deterministic MCQ verification against a mathematically validated key."""
    validate_question(question)
    if option_id not in {option.id for option in question.options}:
        raise ValueError("Unknown answer option.")
    return option_id == question.correct_option_id


def feedback(question: InternalQuestion, misconception: str | None) -> str:
    raise NotImplementedError("Implement indices_logs manual feedback.")


def teaching_recommendation(misconception: str) -> str:
    raise NotImplementedError("Implement indices_logs teaching recommendations.")