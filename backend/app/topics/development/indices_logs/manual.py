from app.contracts import InternalQuestion
import random
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

