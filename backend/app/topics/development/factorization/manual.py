"""Bopage: deterministic mathematics, question generation, and validation for factorization."""
import random
import re
from typing import NamedTuple
from uuid import uuid4

from sympy import Symbol, expand, simplify

from app.contracts import InternalOption, InternalQuestion
from app.safe_symbolic import parse_math

TOPIC_ID = "factorization"
x = Symbol("x")

MISCONCEPTIONS = {
    "SIGN_ERROR": "A factor has an incorrect sign, resulting in an incorrect middle term or constant.",
    "WRONG_FACTOR_PAIR": "Selected a factor pair of the constant term that does not sum to the middle coefficient.",
    "SUM_PRODUCT_CONFUSION": "Confused the sum and product of the roots, or directly used coefficients as factor terms.",
    "COEFFICIENT_FACTOR_MISALLOCATION": "Associated the leading coefficient with the wrong linear factor.",
    "SQUARES_SQUARE_ROOT_ERROR": "Failed to take the square root of the constant term in a difference of two squares.",
}


def _format_factor(a: int, b: int) -> str:
    """Format (ax + b) friendly string."""
    x_part = "x" if a == 1 else ("-x" if a == -1 else f"{a}x")
    if b > 0:
        return f"({x_part} + {b})"
    if b < 0:
        return f"({x_part} - {abs(b)})"
    return f"({x_part})"


def _format_product(factors: tuple[tuple[int, int], tuple[int, int]]) -> str:
    """Format product of two linear factors in canonical sorted order."""
    (a1, b1), (a2, b2) = factors
    f1, f2 = (a1, b1), (a2, b2)
    if (f1[0], f1[1]) > (f2[0], f2[1]):
        f1, f2 = f2, f1
    return f"{_format_factor(f1[0], f1[1])}{_format_factor(f2[0], f2[1])}"


def _format_quadratic(a: int, b: int, c: int) -> str:
    """Format ax^2 + bx + c as a clean algebra string."""
    if a == 1:
        parts = ["x^2"]
    elif a == -1:
        parts = ["-x^2"]
    else:
        parts = [f"{a}x^2"]

    if b != 0:
        if b == 1:
            parts.append("+ x")
        elif b == -1:
            parts.append("- x")
        elif b > 0:
            parts.append(f"+ {b}x")
        else:
            parts.append(f"- {abs(b)}x")

    if c != 0:
        if c > 0:
            parts.append(f"+ {c}")
        else:
            parts.append(f"- {abs(c)}")
    return " ".join(parts)


_FACTOR_REGEX = re.compile(r"^\((-?)(?:(\d+)x|x)\s*([+-])\s*(\d+)\)$")


def _parse_linear_factor(text: str):
    """Safely parse linear factor string without eval or untrusted sympify."""
    m = _FACTOR_REGEX.fullmatch(text.strip())
    if not m:
        raise ValueError(f"Invalid factor format: {text}")
    neg, coeff, sign, num = m.groups()
    a = int(coeff) if coeff else 1
    if neg == "-":
        a = -a
    b = int(num)
    if sign == "-":
        b = -b
    return a * x + b


def _parse_option_expr(text: str):
    """Safely parse option product (ax + b)(cx + d) into an expanded SymPy polynomial."""
    m = re.fullmatch(r"(\(-?[^)]+\))(\(-?[^)]+\))", text.strip())
    if not m:
        raise ValueError(f"Invalid option product format: {text}")
    f1 = _parse_linear_factor(m.group(1))
    f2 = _parse_linear_factor(m.group(2))
    return expand(f1 * f2)


class _Draft(NamedTuple):
    statement: str
    source_expression: str
    correct_expression: str
    explanation: str
    options: list[tuple[str, str | None]]  # [(text, misconception code)]


def _check_draft_internally(options: list[tuple[str, str | None]], expected_poly) -> None:
    texts = [t for t, _ in options]
    if len(options) != 4 or len(set(texts)) != 4:
        raise ValueError("Options must contain exactly 4 unique strings.")
    vals = [_parse_option_expr(t) for t in texts]
    if simplify(vals[0] - expected_poly) != 0:
        raise ValueError("Key is incorrect.")
    for i in range(1, 4):
        if simplify(vals[i] - expected_poly) == 0:
            raise ValueError(f"Distractor {i} equals key.")
        for j in range(i):
            if simplify(vals[i] - vals[j]) == 0:
                raise ValueError(f"Distractor {i} equals distractor {j}.")


def _build_easy_trinomial(rng: random.Random) -> _Draft:
    candidates = [
        (2, 3, 1, 6),
        (2, 4, 1, 8),
        (3, 4, 2, 6),
        (3, 4, 1, 12),
        (2, 6, 3, 4),
        (2, 6, 1, 12),
        (2, 8, 4, 4),
        (3, 6, 2, 9),
        (2, 9, 3, 6),
        (4, 5, 2, 10),
        (2, 10, 4, 5),
        (3, 8, 4, 6),
        (4, 6, 3, 8),
        (3, 5, 1, 15),
        (2, 7, 1, 14),
    ]
    p, q, p_alt, q_alt = rng.choice(candidates)
    if rng.choice([True, False]):
        p, q = q, p

    b = p + q
    c = p * q
    statement = f"Factorize: {_format_quadratic(1, b, c)}"
    source_expr = f"1*x**2 + ({b})*x + ({c})"
    correct_expr = f"(1*x + ({p}))*(1*x + ({q}))"
    correct_text = _format_product(((1, p), (1, q)))

    alt_text = _format_product(((1, p_alt), (1, q_alt)))
    sign_text = _format_product(((1, -p), (1, -q)))
    sum_prod_text = _format_product(((1, -p), (1, q))) if p != q else _format_product(((1, 1), (1, b)))

    options = [
        (correct_text, None),
        (alt_text, "WRONG_FACTOR_PAIR"),
        (sign_text, "SIGN_ERROR"),
        (sum_prod_text, "SUM_PRODUCT_CONFUSION"),
    ]
    expected_poly = expand((x + p) * (x + q))
    _check_draft_internally(options, expected_poly)

    p_min, q_max = min(p, q), max(p, q)
    explanation = (
        f"Find two numbers that multiply to {c} and add to {b}: "
        f"{p_min} × {q_max} = {c} and {p_min} + {q_max} = {b}. "
        f"The factors are {correct_text}."
    )
    return _Draft(statement, source_expr, correct_expr, explanation, options)


def _build_easy_difference_of_squares(rng: random.Random) -> _Draft:
    d = rng.choice([2, 3, 4, 5, 6, 7, 8, 9])
    c = d * d
    statement = f"Factorize: {_format_quadratic(1, 0, -c)}"
    source_expr = f"1*x**2 + (-{c})"
    correct_expr = f"(1*x - ({d}))*(1*x + ({d}))"
    correct_text = _format_product(((1, -d), (1, d)))

    options = [
        (correct_text, None),
        (_format_product(((1, -d), (1, -d))), "SIGN_ERROR"),
        (_format_product(((1, -c), (1, c))), "SQUARES_SQUARE_ROOT_ERROR"),
        (_format_product(((1, d), (1, d))), "SUM_PRODUCT_CONFUSION"),
    ]
    expected_poly = expand((x - d) * (x + d))
    _check_draft_internally(options, expected_poly)

    explanation = (
        f"Apply the difference of two squares identity a^2 - b^2 = (a - b)(a + b): "
        f"x^2 - {d}^2 = {correct_text}."
    )
    return _Draft(statement, source_expr, correct_expr, explanation, options)


def _build_medium_trinomial(rng: random.Random) -> _Draft:
    candidates = [
        (4, 2, 8, 1),
        (5, 2, 10, 1),
        (6, 2, 4, 3),
        (6, 3, 9, 2),
        (5, 3, 15, 1),
        (4, 3, 6, 2),
        (7, 2, 14, 1),
        (6, 4, 8, 3),
    ]
    p, q, p_alt, q_alt = rng.choice(candidates)
    case = rng.choice(["pos_neg", "neg_pos", "both_neg"])
    if case == "pos_neg":
        b = p - q
        c = -(p * q)
        correct_text = _format_product(((1, p), (1, -q)))
        correct_expr = f"(1*x + ({p}))*(1*x + ({-q}))"
        wrong_sign = _format_product(((1, -p), (1, q)))
        wrong_pair = _format_product(((1, p_alt), (1, -q_alt)))
        wrong_sum_prod = _format_product(((1, -p), (1, -q)))
        expected_poly = expand((x + p) * (x - q))
    elif case == "neg_pos":
        b = -(p - q)
        c = -(p * q)
        correct_text = _format_product(((1, -p), (1, q)))
        correct_expr = f"(1*x + ({-p}))*(1*x + ({q}))"
        wrong_sign = _format_product(((1, p), (1, -q)))
        wrong_pair = _format_product(((1, -p_alt), (1, q_alt)))
        wrong_sum_prod = _format_product(((1, p), (1, q)))
        expected_poly = expand((x - p) * (x + q))
    else:
        b = -(p + q)
        c = p * q
        correct_text = _format_product(((1, -p), (1, -q)))
        correct_expr = f"(1*x + ({-p}))*(1*x + ({-q}))"
        wrong_sign = _format_product(((1, p), (1, q)))
        wrong_pair = _format_product(((1, -p_alt), (1, -q_alt)))
        wrong_sum_prod = _format_product(((1, -p), (1, q)))
        expected_poly = expand((x - p) * (x - q))

    statement = f"Factorize: {_format_quadratic(1, b, c)}"
    source_expr = f"1*x**2 + ({b})*x + ({c})"
    options = [
        (correct_text, None),
        (wrong_pair, "WRONG_FACTOR_PAIR"),
        (wrong_sign, "SIGN_ERROR"),
        (wrong_sum_prod, "SUM_PRODUCT_CONFUSION"),
    ]
    _check_draft_internally(options, expected_poly)

    explanation = (
        f"Find two numbers that multiply to {c} and add to {b}. "
        f"The required factors are {correct_text}."
    )
    return _Draft(statement, source_expr, correct_expr, explanation, options)


def _build_hard_question(rng: random.Random) -> _Draft:
    sub = rng.choice(["non_monic_pos", "non_monic_neg", "diff_squares_coeff"])
    if sub == "non_monic_pos":
        candidates = [
            (2, 1, 3), (2, 1, 4), (2, 1, 5), (2, 3, 1), (2, 3, 2), (2, 3, 4), (2, 3, 5),
            (3, 1, 2), (3, 1, 4), (3, 1, 5), (3, 2, 1), (3, 2, 4), (3, 2, 5),
        ]
        a, p, q = rng.choice(candidates)
        b = a * q + p
        c = p * q
        statement = f"Factorize: {_format_quadratic(a, b, c)}"
        source_expr = f"{a}*x**2 + ({b})*x + ({c})"
        correct_expr = f"({a}*x + ({p}))*(1*x + ({q}))"
        correct_text = _format_product(((a, p), (1, q)))
        misallocated_text = _format_product(((1, p), (a, q)))
        sign_text = _format_product(((a, -p), (1, -q)))
        alt_text = _format_product(((a, p + 1), (1, q + 1)))

        options = [
            (correct_text, None),
            (misallocated_text, "COEFFICIENT_FACTOR_MISALLOCATION"),
            (sign_text, "SIGN_ERROR"),
            (alt_text, "WRONG_FACTOR_PAIR"),
        ]
        expected_poly = expand((a * x + p) * (x + q))
        _check_draft_internally(options, expected_poly)

        explanation = (
            f"Split the middle term {b}x into {p}x and {a*q}x: "
            f"{a}x^2 + {p}x + {a*q}x + {c} = {correct_text}."
        )
        return _Draft(statement, source_expr, correct_expr, explanation, options)

    if sub == "non_monic_neg":
        candidates = [
            (2, 1, 3), (2, 1, 4), (2, 1, 5), (2, 3, 1), (2, 3, 2), (2, 3, 4),
            (3, 1, 2), (3, 1, 4), (3, 2, 1), (3, 2, 4),
        ]
        a, p, q = rng.choice(candidates)
        b = a * q - p
        c = -(p * q)
        statement = f"Factorize: {_format_quadratic(a, b, c)}"
        source_expr = f"{a}*x**2 + ({b})*x + ({c})"
        correct_expr = f"({a}*x + ({-p}))*(1*x + ({q}))"
        correct_text = _format_product(((a, -p), (1, q)))
        misallocated_text = _format_product(((1, -p), (a, q)))
        sign_text = _format_product(((a, p), (1, -q)))
        alt_text = _format_product(((a, -p - 1), (1, q + 1)))

        options = [
            (correct_text, None),
            (misallocated_text, "COEFFICIENT_FACTOR_MISALLOCATION"),
            (sign_text, "SIGN_ERROR"),
            (alt_text, "WRONG_FACTOR_PAIR"),
        ]
        expected_poly = expand((a * x - p) * (x + q))
        _check_draft_internally(options, expected_poly)

        explanation = (
            f"Split the middle term {b}x into -{p}x and {a*q}x: "
            f"{a}x^2 - {p}x + {a*q}x - {p*q} = {correct_text}."
        )
        return _Draft(statement, source_expr, correct_expr, explanation, options)

    # Difference of squares with leading coefficient: a^2 x^2 - d^2
    a = rng.choice([2, 3])
    d = rng.choice([1, 3, 5])
    a2 = a * a
    d2 = d * d
    statement = f"Factorize: {_format_quadratic(a2, 0, -d2)}"
    source_expr = f"{a2}*x**2 + (-{d2})"
    correct_expr = f"({a}*x + ({-d}))*({a}*x + ({d}))"
    correct_text = _format_product(((a, -d), (a, d)))
    sign_text = _format_product(((a, -d), (a, -d)))
    misallocated_text = _format_product(((a2, -d), (1, d)))
    sqrt_err_text = _format_product(((a, -d2), (a, d2)))

    options = [
        (correct_text, None),
        (misallocated_text, "COEFFICIENT_FACTOR_MISALLOCATION"),
        (sign_text, "SIGN_ERROR"),
        (sqrt_err_text, "SQUARES_SQUARE_ROOT_ERROR"),
    ]
    expected_poly = expand((a * x - d) * (a * x + d))
    _check_draft_internally(options, expected_poly)

    explanation = (
        f"Apply the difference of two squares identity: "
        f"({a}x)^2 - {d}^2 = {correct_text}."
    )
    return _Draft(statement, source_expr, correct_expr, explanation, options)


def _generate_with_retry(builder, rng: random.Random, tries: int = 20) -> _Draft:
    for _ in range(tries):
        try:
            return builder(rng)
        except ValueError:
            continue
    raise RuntimeError("Could not generate a valid factorization question.")


def generate_question(difficulty: str, rng: random.Random | None = None) -> InternalQuestion:
    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("Difficulty must be easy, medium, or hard.")
    rng = rng or random.SystemRandom()

    if difficulty == "easy":
        builder = rng.choice([_build_easy_trinomial, _build_easy_difference_of_squares])
    elif difficulty == "medium":
        builder = _build_medium_trinomial
    else:
        builder = _build_hard_question

    draft = _generate_with_retry(builder, rng)

    correct_option_id = str(uuid4())
    identified = [
        (correct_option_id if code is None else str(uuid4()), text, code)
        for text, code in draft.options
    ]
    rng.shuffle(identified)
    options = [
        InternalOption(id=opt_id, text=text, misconception=code)
        for opt_id, text, code in identified
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


def _parse_expression(text: str):
    cleaned = text.strip()
    if re.fullmatch(r"(\(-?[^)]+\))(\(-?[^)]+\))", cleaned):
        return _parse_option_expr(cleaned)
    cleaned = re.sub(r"\)\s*\(", ")*(", cleaned)
    return expand(parse_math(cleaned))


def validate_question(question: InternalQuestion) -> None:
    """Independently verify the question mathematically without eval or untrusted string execution."""
    if len(question.options) != 4:
        raise ValueError("Exactly 4 options are required.")

    option_ids = [opt.id for opt in question.options]
    if len(set(option_ids)) != 4:
        raise ValueError("Option IDs must be unique.")

    option_texts = [opt.text for opt in question.options]
    if len(set(option_texts)) != 4:
        raise ValueError("Option texts must be unique.")

    if question.correct_option_id not in option_ids:
        raise ValueError("correct_option_id must match one of the options.")

    correct_options = [opt for opt in question.options if opt.id == question.correct_option_id]
    if len(correct_options) != 1 or correct_options[0].misconception is not None:
        raise ValueError("Correct option must have misconception=None.")

    for opt in question.options:
        if opt.id != question.correct_option_id:
            if not opt.misconception or opt.misconception not in MISCONCEPTIONS:
                raise ValueError(f"Distractor has invalid misconception code: {opt.misconception}")

    expected_poly = _parse_expression(question.source_expression)
    correct_poly = _parse_expression(question.correct_expression)
    if simplify(expected_poly - correct_poly) != 0:
        raise ValueError("source_expression and correct_expression are not mathematically equivalent.")

    option_polys = []
    for opt in question.options:
        poly = _parse_option_expr(opt.text)
        option_polys.append(poly)
        is_key = opt.id == question.correct_option_id
        is_equal = simplify(poly - expected_poly) == 0
        if is_key != is_equal:
            raise ValueError(f"Option {opt.text} key agreement mismatch.")

    for i in range(len(option_polys)):
        for j in range(i + 1, len(option_polys)):
            if simplify(option_polys[i] - option_polys[j]) == 0:
                raise ValueError(f"Duplicate option mathematical value between {i} and {j}.")


def verify_answer(question: InternalQuestion, option_id: str) -> bool:
    """Deterministic MCQ verification against a mathematically validated key."""
    validate_question(question)
    if option_id not in {option.id for option in question.options}:
        raise ValueError("Unknown answer option.")
    return option_id == question.correct_option_id


def feedback(question: InternalQuestion, misconception: str | None) -> str:
    """Return trusted worked steps and misconception feedback."""
    if misconception is None:
        return "Correct. You identified the correct factors of the quadratic expression. " + question.explanation

    messages = {
        "SIGN_ERROR": "You may have made a sign error when finding the factor pair or signs. Review signed multiplication and addition. ",
        "WRONG_FACTOR_PAIR": "You selected factors that multiply to the constant term but do not add to the middle term coefficient. ",
        "SUM_PRODUCT_CONFUSION": "You may have confused the sum and product of the terms, or directly used coefficients as factor constants. ",
        "COEFFICIENT_FACTOR_MISALLOCATION": "You associated the leading coefficient with the wrong factor, altering the middle term upon expansion. ",
        "SQUARES_SQUARE_ROOT_ERROR": "In a difference of two squares, remember to take the square root of the constant term. ",
    }
    return messages.get(misconception, "Review quadratic factorization steps. ") + question.explanation


def teaching_recommendation(misconception: str) -> str:
    """Map diagnostic misconception codes to concrete next-class pedagogical interventions."""
    recommendations = {
        "SIGN_ERROR": "Review multiplication and addition of directed numbers, then practice factorizing quadratics with negative coefficients.",
        "WRONG_FACTOR_PAIR": "List all integer factor pairs of the constant term and check their sums systematically before writing factors.",
        "SUM_PRODUCT_CONFUSION": "Emphasize that the factor constants must MULTIPLY to the constant term 'c' and ADD to the middle coefficient 'b'.",
        "COEFFICIENT_FACTOR_MISALLOCATION": "When factorizing ax^2 + bx + c, use splitting the middle term and factor by grouping to place coefficients correctly.",
        "SQUARES_SQUARE_ROOT_ERROR": "Review the difference of two squares rule a^2 - b^2 = (a - b)(a + b), identifying the square roots of both terms.",
    }
    return recommendations.get(misconception, "Review quadratic factorization with another worked example.")


def verification_feedback(question: InternalQuestion, misconception: str | None, correct: bool) -> tuple[list[str], list[str]]:
    """Grounded feedback options for answer verification service."""
    concepts = {
        "SIGN_ERROR": "Possible misconception: a sign error in the factors causing an incorrect middle term or constant.",
        "WRONG_FACTOR_PAIR": "Possible misconception: choosing a factor pair that satisfies the product but not the required sum.",
        "SUM_PRODUCT_CONFUSION": "Possible misconception: confusing the sum and product conditions for quadratic factorization.",
        "COEFFICIENT_FACTOR_MISALLOCATION": "Possible misconception: placing the leading coefficient in the wrong linear bracket.",
        "SQUARES_SQUARE_ROOT_ERROR": "Possible misconception: using the square instead of the square root in a difference of two squares.",
    }
    text = (
        "Correct answer. All terms and signs match the quadratic expression."
        if correct
        else concepts.get(misconception, "Incorrect answer. The selection alone does not establish a particular misconception.")
    )
    return (
        [text + " " + question.explanation],
        [
            "Check that the product of the constants equals the last term and their sum gives the middle coefficient upon expansion."
        ],
    )
