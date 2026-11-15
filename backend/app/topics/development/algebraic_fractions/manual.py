"""Fernando: deterministic mathematics and fallback. No completed math is supplied."""
import ast
import random
import re
from uuid import uuid4
from sympy import Integer, Symbol, cancel, sqf_part
from app.contracts import InternalOption, InternalQuestion


def _clean_math_text(text: str) -> str:
    """Normalize user-facing math syntax before AST parsing."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Expression must be a non-empty string.")

    cleaned = text.strip().replace('^', '**').replace('−', '-').replace('×', '*').replace('÷', '/')
    cleaned = re.sub(r'(\d)\s*([a-zA-Z])', r'\1*\2', cleaned)
    cleaned = re.sub(r'(\))\s*(\()', r'\1*\2', cleaned)
    cleaned = re.sub(r'(\d)\s*(\()', r'\1*\2', cleaned)
    cleaned = re.sub(r'([a-zA-Z])\s*(\()', r'\1*\2', cleaned)
    return cleaned


def _as_linear(coeff: int, const: int) -> str:
    """Format `coeff*x + const` as a clean algebraic expression string."""
    x_part = "x" if coeff == 1 else f"{coeff}*x"
    if const > 0:
        return f"{x_part} + {const}"
    elif const < 0:
        return f"{x_part} - {abs(const)}"
    return x_part


def _safe_convert_ast(node, symbols: dict[str, Symbol]):
    """Recursively convert bounded AST nodes to SymPy expressions without eval/sympify."""
    if isinstance(node, ast.Constant) and type(node.value) is int and abs(node.value) <= 10000:
        return Integer(node.value)
    if isinstance(node, ast.Name) and node.id in symbols:
        return symbols[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        val = _safe_convert_ast(node.operand, symbols)
        return -val if isinstance(node.op, ast.USub) else val
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Pow):
            if not isinstance(node.right, ast.Constant) or type(node.right.value) is not int or not 0 <= node.right.value <= 6:
                raise ValueError("Unsupported exponent")
        left = _safe_convert_ast(node.left, symbols)
        right = _safe_convert_ast(node.right, symbols)
        if isinstance(node.op, ast.Add): return left + right
        if isinstance(node.op, ast.Sub): return left - right
        if isinstance(node.op, ast.Mult): return left * right
        if isinstance(node.op, ast.Div):
            if right == 0 or cancel(right) == 0:
                raise ValueError("Expression has an identically zero denominator")
            return left / right
        if isinstance(node.op, ast.Pow): return left ** right
    raise ValueError("Unsupported expression syntax")


def _safe_parse_expr(text: str):
    """Safely parse mathematical text into a SymPy expression without eval or sympify."""
    cleaned = _clean_math_text(text)
    if len(cleaned) > 200 or not re.fullmatch(r"[A-Za-z0-9_+*/().\s-]+", cleaned):
        raise ValueError("Unsupported expression")
    try:
        tree = ast.parse(cleaned, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid mathematical syntax {text!r}: {exc}") from exc

    if sum(1 for _ in ast.walk(tree)) > 80:
        raise ValueError("Expression too complex")
    if sum(isinstance(n, ast.Pow) for n in ast.walk(tree)) > 2:
        raise ValueError("Too many powers")

    var_names = tuple(sorted(set(re.findall(r'\b[a-zA-Z]\b', cleaned)))) or ("x",)
    symbols = {name: Symbol(name) for name in var_names}
    try:
        parsed = _safe_convert_ast(tree.body, symbols)
    except Exception as exc:
        raise ValueError(f"Invalid or unsafe mathematical expression {text!r}: {exc}") from exc
    return parsed


def _extract_ast_denominators(text: str):
    """Traverse AST to extract all denominator zero conditions before SymPy division evaluation.

    For each division A/B, B itself is not added directly if it is a rational expression.
    Instead, its numerator is taken as the zero condition for the outer division (B == 0 <=> numer(B) == 0),
    while the AST traversal separately collects restrictions from divisions inside B.
    """
    cleaned = _clean_math_text(text)
    if len(cleaned) > 200 or not re.fullmatch(r"[A-Za-z0-9_+*/().\s-]+", cleaned):
        raise ValueError("Unsupported expression")
    try:
        tree = ast.parse(cleaned, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid mathematical syntax {text!r}: {exc}") from exc

    if sum(1 for _ in ast.walk(tree)) > 80:
        raise ValueError("Expression too complex")
    if sum(isinstance(n, ast.Pow) for n in ast.walk(tree)) > 2:
        raise ValueError("Too many powers")

    var_names = tuple(sorted(set(re.findall(r'\b[a-zA-Z]\b', cleaned)))) or ("x",)
    symbols = {name: Symbol(name) for name in var_names}

    denoms = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            b_sym = _safe_convert_ast(node.right, symbols)
            b_can = cancel(b_sym)
            numer_b, _ = b_can.as_numer_denom()
            if numer_b == 0:
                raise ValueError("Expression has an identically zero denominator")
            if numer_b.has(Symbol):
                denoms.append(numer_b)

    if not denoms:
        return Integer(1)
    prod = Integer(1)
    for d in denoms:
        prod *= d
    return prod


def _check_domain_equivalence(source_text: str, answer_text: str) -> None:
    """Compare source and answer denominator restrictions in both directions."""
    d_source = _extract_ast_denominators(source_text)
    d_answer = _extract_ast_denominators(answer_text)

    source_has_var = d_source.has(Symbol)
    answer_has_var = d_answer.has(Symbol)

    if source_has_var and not answer_has_var:
        raise ValueError("Answer loses an excluded denominator value.")
    if answer_has_var and not source_has_var:
        raise ValueError("Answer adds an unsupported excluded denominator value.")
    if not source_has_var and not answer_has_var:
        return

    sqf_src = sqf_part(d_source)
    sqf_ans = sqf_part(d_answer)

    # 1. Answer must not lose any excluded denominator value present in source
    rem_lost = cancel(sqf_src / sqf_ans)
    num_lost, _ = rem_lost.as_numer_denom()
    if num_lost.has(Symbol):
        raise ValueError("Answer loses an excluded denominator value.")

    # 2. Answer must not add any unsupported excluded denominator value
    rem_added = cancel(sqf_ans / sqf_src)
    num_added, _ = rem_added.as_numer_denom()
    if num_added.has(Symbol):
        raise ValueError("Answer adds an unsupported excluded denominator value.")


class ParameterSpaceExhaustedError(RuntimeError):
    """Raised when all parameter combinations for a family have been exhausted."""
    pass


def get_all_valid_parameters(difficulty: str) -> list[tuple]:
    """Return all valid parameter tuples for the given difficulty family.

    Easy: 1 <= b < a <= 9 and a != 3*b (exactly 33 valid pairs)
    Medium: 2 <= k <= 4, 1 <= b < a <= 6 (exactly 45 valid triples)
    Hard: 1 <= b < d <= 6 and 1 <= c < a <= 5 (exactly 150 valid 4-tuples)
    """
    if difficulty == "easy":
        return [(a, b) for a in range(2, 10) for b in range(1, a) if a != 3 * b]
    elif difficulty == "medium":
        return [(a, b, k) for k in range(2, 5) for a in range(2, 7) for b in range(1, a)]
    elif difficulty == "hard":
        return [
            (a, b, c, d)
            for b in range(1, 6)
            for d in range(b + 1, 7)
            for c in range(1, 5)
            for a in range(c + 1, 6)
        ]
    raise ValueError(f"Invalid difficulty: {difficulty!r}")


def extract_question_parameters(question: InternalQuestion) -> tuple[str, tuple]:
    """Parse difficulty family and parameter values from an InternalQuestion."""
    clean_src = _clean_math_text(question.source_expression)
    norm_src = re.sub(r"\s+", "", clean_src)

    m = re.fullmatch(r"(\d+)/x\+(\d+)/x", norm_src)
    if m:
        return "easy", (int(m.group(1)), int(m.group(2)))

    m = re.fullmatch(r"(\d+)/x-(\d+)/\(?(\d+)\*?x\)?", norm_src)
    if m:
        return "medium", (int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = re.fullmatch(r"(\d+)/\(x\+(\d+)\)-(\d+)/\(x\+(\d+)\)", norm_src)
    if m:
        return "hard", (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))

    raise ValueError(f"Unrecognized question family for source expression: {question.source_expression!r}")


def build_question_from_parameters(
    difficulty: str,
    params: tuple,
    rng: random.Random | None = None,
) -> InternalQuestion:
    """Build and validate an InternalQuestion from verified parameters."""
    r = rng or random.SystemRandom()

    if difficulty == "easy":
        a, b = params
        statement = f"Simplify: {a}/x + {b}/x (where x != 0)"
        source_expression = f"{a}/x + {b}/x"
        correct_expression = f"{a + b}/x"
        explanation = (
            f"The fractions have a common denominator x. Add the numerators: "
            f"({a} + {b})/x = {a + b}/x (where x != 0)."
        )
        raw_options = [
            (f"{a + b}/x", None),
            (f"{a + b}/(2*x)", "DENOMINATOR_ADDITION"),
            (f"{a * b}/x", "NUMERATOR_OPERATION_CONFUSION"),
            (f"{a - b}/x", "SIGN_ERROR"),
        ]

    elif difficulty == "medium":
        a, b, k = params
        statement = f"Simplify: {a}/x - {b}/({k}*x) (where x != 0)"
        source_expression = f"{a}/x - {b}/({k}*x)"
        correct_expression = f"{k * a - b}/({k}*x)"
        explanation = (
            f"The least common denominator of x and {k}x is {k}x. Scale the first fraction: "
            f"({k}*{a} - {b})/({k}x) = ({k * a} - {b})/({k}x) = {k * a - b}/({k}x) (where x != 0)."
        )
        raw_options = [
            (f"{k * a - b}/({k}*x)", None),
            (f"{a - b}/({k + 1}*x)", "DENOMINATOR_ADDITION"),
            (f"{a - b}/({k}*x)", "UNSCALED_NUMERATOR"),
            (f"{k * a + b}/({k}*x)", "SIGN_ERROR"),
        ]

    elif difficulty == "hard":
        a, b, c, d = params
        statement = f"Simplify: {a}/(x + {b}) - {c}/(x + {d}) (where x != -{b} and x != -{d})"
        source_expression = f"{a}/(x + {b}) - {c}/(x + {d})"
        correct_expression = f"({_as_linear(a - c, a * d - c * b)})/((x + {b})*(x + {d}))"
        explanation = (
            f"The common denominator is (x + {b})(x + {d}). Expand and subtract the numerators: "
            f"[{a}(x + {d}) - {c}(x + {b})]/[(x + {b})(x + {d})] = "
            f"[{a}x + {a * d} - {c}x - {c * b}]/[(x + {b})(x + {d})] = "
            f"({_as_linear(a - c, a * d - c * b)})/((x + {b})(x + {d})) (where x != -{b} and x != -{d})."
        )
        raw_options = [
            (f"({_as_linear(a - c, a * d - c * b)})/((x + {b})*(x + {d}))", None),
            (f"({_as_linear(a - c, a * d + c * b)})/((x + {b})*(x + {d}))", "SIGN_DISTRIBUTION_ERROR"),
            (f"{a - c}/(2*x + {b + d})", "DENOMINATOR_ADDITION"),
            (f"{a - c}/((x + {b})*(x + {d}))", "UNSCALED_NUMERATOR"),
        ]

    else:
        raise ValueError(f"Invalid difficulty: {difficulty!r}")

    correct_id = str(uuid4())
    options = [
        InternalOption(
            id=correct_id if label is None else str(uuid4()),
            text=text,
            misconception=label,
        )
        for text, label in raw_options
    ]
    r.shuffle(options)

    question = InternalQuestion(
        id=str(uuid4()),
        topic_id="algebraic_fractions",
        difficulty=difficulty,
        statement=statement,
        options=options,
        correct_option_id=correct_id,
        explanation=explanation,
        source_expression=source_expression,
        correct_expression=correct_expression,
    )
    validate_question(question)
    return question


def generate_remediation_variation(
    difficulty: str,
    exclude_params: set[tuple] | None = None,
    rng: random.Random | None = None,
) -> InternalQuestion:
    """Generate an unseen remediation question variation from the same family."""
    exclude = set(exclude_params or ())
    valid_pool = [p for p in get_all_valid_parameters(difficulty) if p not in exclude]
    if not valid_pool:
        raise ParameterSpaceExhaustedError(
            f"All parameter combinations for {difficulty} algebraic fractions have been exhausted ({len(exclude)} used)."
        )
    r = rng or random.SystemRandom()
    chosen_params = r.choice(valid_pool)
    return build_question_from_parameters(difficulty, chosen_params, rng=r)


def generate_question(difficulty: str, rng: random.Random | None = None) -> InternalQuestion:
    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("Difficulty must be easy, medium, or hard.")

    r = rng or random.SystemRandom()
    valid_pool = get_all_valid_parameters(difficulty)
    chosen_params = r.choice(valid_pool)
    return build_question_from_parameters(difficulty, chosen_params, rng=r)


def validate_question(question: InternalQuestion) -> None:
    # 1. Structural validation
    if not isinstance(question, InternalQuestion):
        raise ValueError("Question must be an instance of InternalQuestion.")
    if question.topic_id != "algebraic_fractions":
        raise ValueError(f"Expected topic_id 'algebraic_fractions', got {question.topic_id!r}.")
    if question.difficulty not in {"easy", "medium", "hard"}:
        raise ValueError(f"Invalid difficulty {question.difficulty!r}; expected 'easy', 'medium', or 'hard'.")
    if not question.id or not isinstance(question.id, str):
        raise ValueError("Question id must be a non-empty string.")
    if not question.statement or not isinstance(question.statement, str) or not question.statement.strip():
        raise ValueError("Question statement must be a non-empty string.")
    if not question.explanation or not isinstance(question.explanation, str) or not question.explanation.strip():
        raise ValueError("Question explanation must be a non-empty string.")
    if not question.source_expression or not isinstance(question.source_expression, str) or not question.source_expression.strip():
        raise ValueError("source_expression must be a non-empty string.")
    if not question.correct_expression or not isinstance(question.correct_expression, str) or not question.correct_expression.strip():
        raise ValueError("correct_expression must be a non-empty string.")

    # 2. Options validation
    if not isinstance(question.options, list) or len(question.options) != 4:
        raise ValueError("Question must have exactly four options.")

    for opt in question.options:
        if not isinstance(opt, InternalOption):
            raise ValueError("All options must be instances of InternalOption.")
        if not opt.id or not isinstance(opt.id, str):
            raise ValueError("Option id must be a non-empty string.")
        if not opt.text or not isinstance(opt.text, str) or not opt.text.strip():
            raise ValueError("Option text must be a non-empty string.")

    option_ids = [opt.id for opt in question.options]
    if len(set(option_ids)) != 4:
        raise ValueError("All four option IDs must be unique.")

    option_texts = [opt.text.strip() for opt in question.options]
    if len(set(option_texts)) != 4:
        raise ValueError("All four option texts must be unique.")

    if not question.correct_option_id or not isinstance(question.correct_option_id, str):
        raise ValueError("correct_option_id must be a non-empty string.")

    if question.correct_option_id not in set(option_ids):
        raise ValueError(f"correct_option_id {question.correct_option_id!r} not found in question options.")

    correct_option = next(opt for opt in question.options if opt.id == question.correct_option_id)
    if correct_option.misconception is not None:
        raise ValueError("The correct option must have misconception=None.")

    distractors = [opt for opt in question.options if opt.id != question.correct_option_id]
    if any(d.misconception is None for d in distractors):
        raise ValueError("Distractor options must have a diagnostic misconception code.")

    # 3. Domain restrictions: compare source and correct expression in both directions
    _check_domain_equivalence(question.source_expression, question.correct_expression)

    # 4. Mathematical validation via safe parsing
    source_sym = _safe_parse_expr(question.source_expression)
    correct_sym = _safe_parse_expr(question.correct_expression)

    # Check for identically zero denominators
    _, source_denom = source_sym.as_numer_denom()
    _, correct_denom = correct_sym.as_numer_denom()
    if source_denom == 0 or cancel(source_sym).as_numer_denom()[1] == 0:
        raise ValueError("source_expression has an identically zero denominator.")
    if correct_denom == 0 or cancel(correct_sym).as_numer_denom()[1] == 0:
        raise ValueError("correct_expression has an identically zero denominator.")

    # Source expression must equal correct expression on common domain
    if cancel(source_sym - correct_sym) != 0:
        raise ValueError("source_expression and correct_expression are not mathematically equivalent.")

    # Parse all options safely
    parsed_options = [_safe_parse_expr(opt.text) for opt in question.options]
    for opt, parsed_expr in zip(question.options, parsed_options):
        _, opt_denom = parsed_expr.as_numer_denom()
        if opt_denom == 0 or cancel(parsed_expr).as_numer_denom()[1] == 0:
            raise ValueError(f"Option {opt.id!r} text {opt.text!r} has an identically zero denominator.")

    correct_idx = next(i for i, opt in enumerate(question.options) if opt.id == question.correct_option_id)
    correct_opt_sym = parsed_options[correct_idx]

    # The correct option must match correct_expression and have identical domain restrictions
    _check_domain_equivalence(question.source_expression, question.options[correct_idx].text)
    if cancel(correct_opt_sym - correct_sym) != 0:
        raise ValueError("The option matching correct_option_id is not mathematically equivalent to correct_expression.")

    # Check distractors: none can equal correct_expression, and all must be pairwise distinct
    for idx, (opt, parsed_expr) in enumerate(zip(question.options, parsed_options)):
        if idx != correct_idx:
            if cancel(parsed_expr - correct_sym) == 0:
                raise ValueError(f"Distractor option {opt.id!r} ({opt.text!r}) is mathematically equivalent to the correct expression.")

        # Pairwise distinctness check among all options
        for other_idx in range(idx):
            if cancel(parsed_expr - parsed_options[other_idx]) == 0:
                raise ValueError(
                    f"Option {opt.id!r} ({opt.text!r}) is mathematically equivalent to option "
                    f"{question.options[other_idx].id!r} ({question.options[other_idx].text!r})."
                )


def verify_answer(question: InternalQuestion, option_id: str) -> bool:
    """Deterministic MCQ verification against a mathematically validated key."""
    validate_question(question)
    if option_id not in {option.id for option in question.options}:
        raise ValueError("Unknown answer option.")
    return option_id == question.correct_option_id


def feedback(question: InternalQuestion, misconception: str | None) -> str:
    """Return trusted worked steps and a possible-misconception explanation.

    None is used for correct selections. Never diagnose a misconception as proven.
    """
    if misconception is None:
        return f"Correct. You simplified the algebraic fraction properly. {question.explanation}"

    messages = {
        "DENOMINATOR_ADDITION": (
            "You may have added the denominators directly across fractions. "
            "Remember that fractions can only be combined over a common denominator; "
            "denominators do not add together. "
        ),
        "UNSCALED_NUMERATOR": (
            "You may have converted to a common denominator without scaling the numerator. "
            "When you multiply the denominator by a factor, you must multiply the numerator "
            "by the same factor to maintain equivalence. "
        ),
        "SIGN_ERROR": (
            "You may have made a sign error when combining the numerators. "
            "Carefully check whether you should be adding or subtracting the terms. "
        ),
        "SIGN_DISTRIBUTION_ERROR": (
            "You may have forgotten to distribute the negative sign to all terms in the second numerator. "
            "When subtracting a binomial numerator, the negative sign must be distributed across both terms. "
        ),
        "NUMERATOR_OPERATION_CONFUSION": (
            "You may have multiplied the numerators instead of adding or subtracting them. "
            "When adding or subtracting fractions over a common denominator, combine the numerators "
            "using addition or subtraction, not multiplication. "
        ),
    }

    prefix = messages.get(
        misconception,
        "Review the rules for combining and simplifying algebraic fractions. ",
    )
    return f"{prefix}{question.explanation}"


def teaching_recommendation(misconception: str) -> str:
    """Map stable diagnostic codes to specific correction activities, with a safe generic fallback."""
    recommendations = {
        "DENOMINATOR_ADDITION": (
            "Review numerical fraction addition with visual area models to reinforce why denominators do not add, "
            "then transition to algebraic fractions with like denominators (e.g., 1/x + 2/x)."
        ),
        "UNSCALED_NUMERATOR": (
            "Have students practice finding equivalent fractions by multiplying both numerator and denominator "
            "by the necessary scaling factor before combining."
        ),
        "SIGN_ERROR": (
            "Have students write the operation between fractions explicitly and check signed-number addition and "
            "subtraction before combining numerators."
        ),
        "SIGN_DISTRIBUTION_ERROR": (
            "Demonstrate placing parentheses around the entire subtracted numerator, showing step-by-step how the "
            "subtraction sign distributes to every term."
        ),
        "NUMERATOR_OPERATION_CONFUSION": (
            "Contrast fraction addition and fraction multiplication side by side to reinforce when numerators are added "
            "versus when they are multiplied."
        ),
    }

    return recommendations.get(
        misconception,
        "Review algebraic fraction simplification with another worked example and guided practice.",
    )
