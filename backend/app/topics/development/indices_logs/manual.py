from app.contracts import InternalQuestion
import random
import re
from uuid import uuid4
from sympy import Integer
from app.contracts import InternalOption, InternalQuestion

TOPIC_ID = "indices_logs"


# ---------- Part 1: build one product-law question (with checks) ----------

def _build_product_law(rng):
    base = rng.choice([2, 3, 5])
    m = rng.randint(2, 5)
    n = rng.choice([k for k in range(2, 6) if k != m])  # m != n

    # (base, exponent, misconception code)
    raw = [
        (base,        m + n,      None),                    # correct
        (base,        m * n,      "MULTIPLIED_EXPONENTS"),
        (base * base, m + n,      "MULTIPLIED_BASES"),
        (base,        abs(m - n), "SUBTRACTED_EXPONENTS"),
    ]
    expected = Integer(base) ** m * Integer(base) ** n

    values = [Integer(b) ** e for b, e, _ in raw]
    if values[0] != expected:
        raise ValueError("Wrong key.")
    if any(v == expected for v in values[1:]):
        raise ValueError("A distractor equals the correct answer.")
    if len(set(values)) != 4:
        raise ValueError("Duplicate option values.")
    return base, m, n, raw


def _generate_with_retry(rng, tries=20):
    for _ in range(tries):
        try:
            return _build_product_law(rng)
        except ValueError:
            continue
    raise RuntimeError("Could not generate a valid question.")


# ---------- Part 2: required functions ----------

def generate_question(difficulty: str, rng=None) -> InternalQuestion:
    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("Difficulty must be easy, medium, or hard.")
    rng = rng or random.SystemRandom()

    base, m, n, raw = _generate_with_retry(rng)

    correct_option_id = str(uuid4())
    identified = [
        (correct_option_id if code is None else str(uuid4()), b, e, code)
        for b, e, code in raw
    ]
    rng.shuffle(identified)
    options = [
        InternalOption(id=oid, text=f"{b}^{e}", misconception=code)
        for oid, b, e, code in identified
    ]

    explanation = (
        f"Same base, so ADD the exponents: {m} + {n} = {m + n}. "
        f"The answer is {base}^{m + n}."
    )
    return InternalQuestion(
        id=str(uuid4()),
        topic_id=TOPIC_ID,
        difficulty=difficulty,
        statement=f"Simplify: {base}^{m} × {base}^{n}",
        options=options,
        correct_option_id=correct_option_id,
        explanation=explanation,
        source_expression=f"{base}^{m}*{base}^{n}",
        correct_expression=f"{base}^{m + n}",
    )


def validate_question(question: InternalQuestion) -> None:
    raise NotImplementedError("Implement indices_logs mathematical validation.")


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

# ---------- Part 3: independent validation ----------

MAX_BASE = 99
MAX_EXPONENT = 50

_POWER = re.compile(r"(\d+)\^(\d+)")
_PRODUCT = re.compile(r"(\d+)\^(\d+)\*(\d+)\^(\d+)")


def _checked_power(base: int, exponent: int) -> Integer:
    """Safe base^exponent. Huge numbers are rejected so nothing can hang."""
    if not 2 <= base <= MAX_BASE:
        raise ValueError(f"Base {base} is outside the allowed range.")
    if not 0 <= exponent <= MAX_EXPONENT:
        raise ValueError(f"Exponent {exponent} is outside the allowed range.")
    return Integer(base) ** exponent


def _power_value(text: str) -> Integer:
    """Read text like '2^7' with a strict pattern (no eval, no sympify)."""
    match = _POWER.fullmatch(text.strip())
    if not match:
        raise ValueError(f"Unreadable power: {text!r}")
    return _checked_power(int(match[1]), int(match[2]))


def _expected_value(source_expression: str) -> Integer:
    """Work out the true answer from the source expression."""
    match = _PRODUCT.fullmatch(source_expression.strip())
    if not match:
        raise ValueError("Unknown question pattern.")
    b1, m, b2, n = (int(g) for g in match.groups())
    return _checked_power(b1, m) * _checked_power(b2, n)


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

    

