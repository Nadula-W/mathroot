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


_CODES_BY_LAW = {
    "product": {"MULTIPLIED_EXPONENTS", "MULTIPLIED_BASES", "SUBTRACTED_EXPONENTS"},
    "quotient": {"ADDED_EXPONENTS", "DIVIDED_EXPONENTS", "DIVIDED_BASES"},
}


def _parse_source(source_expression: str):
    """Return (law, base, m, n) from a source expression."""
    text = source_expression.strip()
    for law, pattern in (("product", _PRODUCT), ("quotient", _QUOTIENT)):
        match = pattern.fullmatch(text)
        if match:
            b1, m, b2, n = (int(g) for g in match.groups())
            if b1 != b2:
                raise ValueError("Both powers must have the same base.")
            return law, b1, m, n
    raise ValueError("Unknown question pattern.")


def _expected_value(source_expression: str):
    """Work out the true answer from the source expression."""
    law, base, m, n = _parse_source(source_expression)
    if law == "product":
        return _checked_power(base, m) * _checked_power(base, n)
    return _checked_power(base, m) / _checked_power(base, n)


def _evidence_value(code: str, base: int, m: int, n: int):
    """The exact wrong value a student gets when they make this mistake."""
    if code == "MULTIPLIED_EXPONENTS":
        return _checked_power(base, m * n)
    if code == "MULTIPLIED_BASES":
        return _checked_power(base * base, m + n)
    if code == "SUBTRACTED_EXPONENTS":
        return _checked_power(base, abs(m - n))
    if code == "ADDED_EXPONENTS":
        return _checked_power(base, m + n)
    if code == "DIVIDED_EXPONENTS":
        return _checked_power(base, m, n)
    if code == "DIVIDED_BASES":
        return Integer(1)  # (base / base) = 1
    raise ValueError(f"Unknown misconception code: {code}")


def explain(source_expression: str) -> str:
    """Trusted explanation text, written by us (never by the AI)."""
    law, base, m, n = _parse_source(source_expression)
    if law == "product":
        return (f"Same base, so ADD the exponents: {m} + {n} = {m + n}. "
                f"The answer is {base}^{m + n}.")
    return (f"Same base, so SUBTRACT the exponents: {m} - {n} = {m - n}. "
            f"The answer is {base}^{m - n}.")


def validate_question(question: InternalQuestion) -> None:
    options = question.options
    ids = [option.id for option in options]

    if len(options) != 4:
        raise ValueError("Exactly 4 options are required.")
    if len(set(ids)) != 4:
        raise ValueError("Option ids must be unique.")
    if question.correct_option_id not in ids:
        raise ValueError("correct_option_id is not one of the options.")

    law, base, m, n = _parse_source(question.source_expression)
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
        if not is_key:
            code = option.misconception
            if code not in _CODES_BY_LAW[law]:
                raise ValueError(f"Code {code} does not belong to the {law} law.")
            if value != _evidence_value(code, base, m, n):
                raise ValueError(f"Option {option.text} is not evidence for {code}.")
        values.append(value)

    if len(set(values)) != 4:
        raise ValueError("Duplicate option values.")


def verify_answer(question: InternalQuestion, option_id: str) -> bool:
    """Deterministic MCQ verification against a mathematically validated key."""
    validate_question(question)
    if option_id not in {option.id for option in question.options}:
        raise ValueError("Unknown answer option.")
    return option_id == question.correct_option_id


# ---------- Part 4: diagnosis text ----------

MISCONCEPTIONS = {
    "MULTIPLIED_EXPONENTS": "The exponents were multiplied instead of added.",
    "MULTIPLIED_BASES": "The bases were multiplied as well as the exponents being added.",
    "SUBTRACTED_EXPONENTS": "The exponents were subtracted when they should be added.",
    "ADDED_EXPONENTS": "The exponents were added when they should be subtracted.",
    "DIVIDED_EXPONENTS": "The exponents were divided instead of subtracted.",
    "DIVIDED_BASES": "The bases were divided instead of keeping the same base.",
}

_FEEDBACK = {
    "MULTIPLIED_EXPONENTS": "You may have multiplied the exponents. When you MULTIPLY powers with the same base, you add the exponents.",
    "MULTIPLIED_BASES": "You may have multiplied the bases. The base stays the same; only the exponents change.",
    "SUBTRACTED_EXPONENTS": "You may have subtracted the exponents. Subtracting is for division, not for multiplication.",
    "ADDED_EXPONENTS": "You may have added the exponents. When you DIVIDE powers with the same base, you subtract the exponents.",
    "DIVIDED_EXPONENTS": "You may have divided the exponents. Divide the powers by subtracting the exponents.",
    "DIVIDED_BASES": "You may have divided the bases. The base stays the same; only the exponents change.",
}

_RECOMMENDATIONS = {
    "MULTIPLIED_EXPONENTS": "Expand a small example such as 2^2 x 2^3 as 2x2x2x2x2 to show why exponents are added, then practise the product law.",
    "MULTIPLIED_BASES": "Stress that the base is written once: show 2^2 x 2^3 = 2^5, then compare with (2x2)^5.",
    "SUBTRACTED_EXPONENTS": "Contrast the product law (add) and the quotient law (subtract) side by side with two short examples.",
    "ADDED_EXPONENTS": "Expand 6^5 / 6^2 as a fraction and cancel common factors to show the exponents are subtracted.",
    "DIVIDED_EXPONENTS": "Show that dividing powers cancels factors, so the exponents are subtracted, never divided.",
    "DIVIDED_BASES": "Cancel factors in a worked example: the base remains, only the number of factors changes.",
}


def feedback(question: InternalQuestion, misconception: str | None) -> str:
    if misconception is None:
        return "Correct. " + question.explanation
    hint = _FEEDBACK.get(misconception, "Review the laws of indices.")
    return hint + " " + question.explanation


def teaching_recommendation(misconception: str) -> str:
    return _RECOMMENDATIONS.get(
        misconception, "Review the laws of indices with another worked example."
    )