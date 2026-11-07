"""Sadeepa: deterministic mathematics and fallback."""
import random
import re
from functools import lru_cache
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
    statement, source = question_texts("product", base, m, n)
    return _Draft(statement, source, f"{base}^{m + n}", explain(source), options)


def _build_quotient_law(rng) -> _Draft:
    base = rng.choice([2, 3, 5, 6])
    n = rng.randint(2, 4)
    # m > n, and m/n is NOT a whole number, so base^(m/n) really looks like a fraction
    m = rng.choice([k for k in range(n + 1, 9) if k % n != 0])

    options = [
        (f"{base}^{m - n}",   Integer(base) ** (m - n),        None),
        (f"{base}^{m + n}",   Integer(base) ** (m + n),        "ADDED_EXPONENTS"),
        (f"{base}^({m}/{n})", Integer(base) ** Rational(m, n), "DIVIDED_EXPONENTS"),
        (f"1^{m - n}",        Integer(1),                      "DIVIDED_BASES"),
    ]
    _self_check(options, Integer(base) ** m / Integer(base) ** n)
    statement, source = question_texts("quotient", base, m, n)
    return _Draft(statement, source, f"{base}^{m - n}", explain(source), options)


@lru_cache(maxsize=1)
def power_specs() -> list:
    """All (base, m, n) for (base^m)^n whose 4 options are really different."""
    specs = []
    for base in (2, 3, 5, 6):
        for m in range(2, 6):
            for n in range(2, 4):
                if m ** n > MAX_EXPONENT:
                    continue
                values = {
                    Integer(base) ** (m * n),
                    Integer(base) ** (m + n),
                    Integer(n) * Integer(base) ** m,
                    Integer(base) ** (m ** n),
                }
                if len(values) == 4:
                    specs.append((base, m, n))
    return specs


def _build_power_law(rng) -> _Draft:
    base, m, n = rng.choice(power_specs())

    options = [
        (f"{base}^{m * n}",    Integer(base) ** (m * n),        None),
        (f"{base}^{m + n}",    Integer(base) ** (m + n),        "ADDED_EXPONENTS_POWER"),
        (f"{n} × {base}^{m}",  Integer(n) * Integer(base) ** m, "EXPONENT_AS_MULTIPLIER"),
        (f"{base}^{m ** n}",   Integer(base) ** (m ** n),       "POWER_ONLY_ON_EXPONENT"),
    ]
    _self_check(options, (Integer(base) ** m) ** n)
    statement, source = question_texts("power", base, m, n)
    return _Draft(statement, source, f"{base}^{m * n}", explain(source), options)


@lru_cache(maxsize=2)
def conversion_specs(law: str) -> list:
    """All (base, exponent) whose 4 statements are different and only ONE is true."""
    specs = []
    for base in (2, 3, 5, 10):
        for e in range(2, 6):
            if base == e:
                continue
            v = base ** e
            if law == "tolog":
                options = [(base, v, e), (v, base, e), (e, v, base), (base, e, v)]
                truth = [_power_equals(b, r, n) for b, n, r in options]
            else:
                options = [(base, e, v), (e, base, v), (v, e, base), (base, v, e)]
                truth = [_power_equals(b, x, y) for b, x, y in options]
            if truth == [True, False, False, False] and len(set(options)) == 4:
                specs.append((base, e))
    return specs


def _build_tolog_law(rng) -> _Draft:
    """Index form -> log form:  b^e = v   becomes   log_b v = e."""
    base, e = rng.choice(conversion_specs("tolog"))
    v = base ** e

    options = [
        (f"log_{base} {v} = {e}", (base, v, e), None),
        (f"log_{v} {base} = {e}", (v, base, e), "LOG_BASE_AND_NUMBER_SWAPPED"),
        (f"log_{e} {v} = {base}", (e, v, base), "LOG_BASE_AND_RESULT_SWAPPED"),
        (f"log_{base} {e} = {v}", (base, e, v), "LOG_NUMBER_AND_RESULT_SWAPPED"),
    ]
    _self_check(options, (base, v, e))
    statement, source = question_texts("tolog", base, e, v)
    return _Draft(statement, source, options[0][0], explain(source), options)


def _build_toindex_law(rng) -> _Draft:
    """Log form -> index form:  log_b v = e   becomes   b^e = v."""
    base, e = rng.choice(conversion_specs("toindex"))
    v = base ** e

    options = [
        (f"{base}^{e} = {v}", (base, e, v), None),
        (f"{e}^{base} = {v}", (e, base, v), "INDEX_BASE_AND_EXPONENT_SWAPPED"),
        (f"{v}^{e} = {base}", (v, e, base), "INDEX_BASE_AND_VALUE_SWAPPED"),
        (f"{base}^{v} = {e}", (base, v, e), "INDEX_EXPONENT_AND_VALUE_SWAPPED"),
    ]
    _self_check(options, (base, e, v))
    statement, source = question_texts("toindex", base, e, v)
    return _Draft(statement, source, options[0][0], explain(source), options)


@lru_cache(maxsize=4)
def log_specs(law: str) -> list:
    """All (base, m, n) for a log law whose 4 options really are different.

    logvalue: (base, exponent, number)   logsum / logdiff: (base, i, j) for log_b b^i, log_b b^j
    logpower: (base, k, r) for log_b ((b^k)^r)
    """
    if law == "logvalue":
        candidates = [(b, e, b ** e) for b in (2, 3, 5, 10) for e in range(2, 6)]
    elif law == "logsum":
        candidates = [(b, i, j) for b in (2, 3, 5) for i in range(1, 5) for j in range(i + 1, 5)]
    elif law == "logdiff":
        candidates = [(b, i, j) for b in (2, 3, 5) for i in range(2, 6) for j in range(1, i)
                      if Rational(i, j).q in (2, 4, 5)]  # i/j must be a short decimal
    else:
        candidates = [(b, k, r) for b in (2, 3, 5) for k in range(2, 5) for r in range(2, 5)]

    specs = []
    for base, m, n in candidates:
        _, source = question_texts(law, base, m, n)
        values = [_expected_value(source)]
        values += [_evidence_value(code, base, m, n) for code in sorted(_CODES_BY_LAW[law])]
        # "log of a sum / difference" must stay a real log such as log_2 12, not a whole number
        if law in ("logsum", "logdiff") and not any(isinstance(v, tuple) for v in values):
            continue
        if len(set(values)) == 4:
            specs.append((base, m, n))
    return specs


def _build_logvalue_law(rng) -> _Draft:
    """log_b N = ?   where N = b^e."""
    base, e, n = rng.choice(log_specs("logvalue"))

    options = [
        (str(e),           Integer(e),           None),
        (str(n // base),   Integer(n // base),   "DIVIDED_VALUE_BY_BASE"),
        (str(n - base),    Integer(n - base),    "SUBTRACTED_BASE_FROM_VALUE"),
        (str(e - 1),       Integer(e - 1),       "COUNTED_MULTIPLICATION_SIGNS"),
    ]
    _self_check(options, Integer(e))
    statement, source = question_texts("logvalue", base, e, n)
    return _Draft(statement, source, str(e), explain(source), options)


def _build_logsum_law(rng) -> _Draft:
    """log_b M + log_b N   where M = b^i and N = b^j."""
    base, i, j = rng.choice(log_specs("logsum"))
    big_m, big_n = base ** i, base ** j

    options = [
        (str(i + j),                       Integer(i + j),                   None),
        (f"log_{base} {big_m + big_n}",    _log_value(base, big_m + big_n),  "LOG_OF_SUM"),
        (str(i * j),                       Integer(i * j),                   "MULTIPLIED_LOG_VALUES"),
        (str(big_m + big_n),               Integer(big_m + big_n),           "LOGS_IGNORED_NUMBERS_ADDED"),
    ]
    _self_check(options, Integer(i + j))
    statement, source = question_texts("logsum", base, i, j)
    return _Draft(statement, source, str(i + j), explain(source), options)


def _build_logdiff_law(rng) -> _Draft:
    """log_b M - log_b N   where M = b^i and N = b^j (i > j)."""
    base, i, j = rng.choice(log_specs("logdiff"))
    big_m, big_n = base ** i, base ** j
    ratio = Rational(i, j)

    options = [
        (str(i - j),                        Integer(i - j),                    None),
        (f"log_{base} {big_m - big_n}",     _log_value(base, big_m - big_n),   "LOG_OF_DIFFERENCE"),
        (f"{float(ratio):g}",               ratio,                             "DIVIDED_LOG_VALUES"),
        (str(big_m // big_n),               Integer(big_m // big_n),           "LOGS_IGNORED_NUMBERS_DIVIDED"),
    ]
    _self_check(options, Integer(i - j))
    statement, source = question_texts("logdiff", base, i, j)
    return _Draft(statement, source, str(i - j), explain(source), options)


def _build_logpower_law(rng) -> _Draft:
    """log_b ((b^k)^r) = r * k   (the power law)."""
    base, k, r = rng.choice(log_specs("logpower"))

    options = [
        (str(k * r),   Integer(k * r),   None),
        (str(k ** r),  Integer(k ** r),  "LOG_RAISED_TO_POWER"),
        (str(k + r),   Integer(k + r),   "POWER_ADDED_TO_LOG"),
        (str(k),       Integer(k),       "POWER_IGNORED"),
    ]
    _self_check(options, Integer(k * r))
    statement, source = question_texts("logpower", base, k, r)
    return _Draft(statement, source, str(k * r), explain(source), options)


_LAWS = {
    "product": _build_product_law,
    "quotient": _build_quotient_law,
    "power": _build_power_law,
    "tolog": _build_tolog_law,
    "toindex": _build_toindex_law,
    "logvalue": _build_logvalue_law,
    "logsum": _build_logsum_law,
    "logdiff": _build_logdiff_law,
    "logpower": _build_logpower_law,
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


def question_texts(law: str, base: int, m: int, n: int) -> tuple[str, str]:
    """(statement shown to the student, source expression for the validator)."""
    if law == "product":
        return f"Simplify: {base}^{m} × {base}^{n}", f"{base}^{m}*{base}^{n}"
    if law == "quotient":
        return f"Simplify: {base}^{m} ÷ {base}^{n}", f"{base}^{m}/{base}^{n}"
    if law == "power":
        return f"Simplify: ({base}^{m})^{n}", f"({base}^{m})^{n}"
    if law == "tolog":  # m = exponent, n = value
        return f"Write {base}^{m} = {n} in logarithmic form.", f"{base}^{m}={n}"
    if law == "toindex":  # m = exponent, n = value
        return f"Write log_{base} {n} = {m} in index form.", f"log_{base} {n}={m}"
    if law == "logvalue":  # m = exponent, n = number
        return f"Find the value of log_{base} {n}.", f"log_{base} {n}"
    if law == "logsum":  # m = i, n = j  (numbers are base^i and base^j)
        big_m, big_n = base ** m, base ** n
        return (f"Find the value of log_{base} {big_m} + log_{base} {big_n}.",
                f"log_{base} {big_m}+log_{base} {big_n}")
    if law == "logdiff":
        big_m, big_n = base ** m, base ** n
        return (f"Find the value of log_{base} {big_m} - log_{base} {big_n}.",
                f"log_{base} {big_m}-log_{base} {big_n}")
    if law == "logpower":  # m = k, n = r  ->  log_base ((base^k)^r)
        inner = base ** m
        return f"Find the value of log_{base} ({inner}^{n}).", f"log_{base} ({inner}^{n})"
    raise ValueError(f"Unknown law: {law}")


def explain(source_expression: str) -> str:
    """Trusted explanation text, written by us (never by the AI)."""
    law, base, m, n = _parse_source(source_expression)
    if law == "product":
        return (f"Same base, so ADD the exponents: {m} + {n} = {m + n}. "
                f"The answer is {base}^{m + n}.")
    if law == "quotient":
        return (f"Same base, so SUBTRACT the exponents: {m} - {n} = {m - n}. "
                f"The answer is {base}^{m - n}.")
    if law == "power":
        return (f"A power of a power, so MULTIPLY the exponents: {m} × {n} = {m * n}. "
                f"The answer is {base}^{m * n}.")
    if law == "tolog":
        return (f"{base}^{m} = {n} means: the base {base} stays the base of the log, "
                f"the number is {n}, and the exponent {m} is the answer. So log_{base} {n} = {m}.")
    if law == "logvalue":
        return (f"log_{base} {n} asks: which power of {base} gives {n}? "
                f"{base}^{m} = {n}, so the answer is {m}.")
    if law == "logsum":
        return (f"Find each log first: log_{base} {base ** m} = {m} and log_{base} {base ** n} = {n}. "
                f"Then add: {m} + {n} = {m + n}.")
    if law == "logdiff":
        return (f"Find each log first: log_{base} {base ** m} = {m} and log_{base} {base ** n} = {n}. "
                f"Then subtract: {m} - {n} = {m - n}.")
    if law == "logpower":
        return (f"Power law: log_{base} ({base ** m}^{n}) = {n} x log_{base} {base ** m} "
                f"= {n} x {m} = {m * n}.")
    return (f"log_{base} {n} = {m} means: the base {base} stays the base, "
            f"the answer {m} becomes the exponent, and the number {n} is the result. "
            f"So {base}^{m} = {n}.")


# ---------- Part 3: independent validation ----------

MAX_BASE = 99
MAX_EXPONENT = 50
MAX_ROOT = 10

# "2^7", "2^(7/2)"  and  "3 × 2^4"
_POWER = re.compile(r"(\d+)\^(?:(\d+)|\((\d+)/(\d+)\))")
_MULTIPLE = re.compile(r"(\d+)\s*×\s*(\d+)\^(\d+)")
_PRODUCT = re.compile(r"(\d+)\^(\d+)\*(\d+)\^(\d+)")
_QUOTIENT = re.compile(r"(\d+)\^(\d+)/(\d+)\^(\d+)")
_POWER_OF_POWER = re.compile(r"\((\d+)\^(\d+)\)\^(\d+)")
_TOLOG_SOURCE = re.compile(r"(\d{1,6})\^(\d{1,6})=(\d{1,6})")        # 2^5=32
_TOINDEX_SOURCE = re.compile(r"log_(\d{1,6}) (\d{1,6})=(\d{1,6})")    # log_3 81=4
_LOG_STATEMENT = re.compile(r"log_(\d{1,6})\s+(\d{1,6})\s*=\s*(\d{1,6})")
_INDEX_STATEMENT = re.compile(r"(\d{1,6})\^(\d{1,6})\s*=\s*(\d{1,6})")
_LOGVALUE_SOURCE = re.compile(r"log_(\d{1,6}) (\d{1,6})")                          # log_2 32
_LOGSUM_SOURCE = re.compile(r"log_(\d{1,6}) (\d{1,6})\+log_(\d{1,6}) (\d{1,6})")   # log_2 4+log_2 8
_LOGDIFF_SOURCE = re.compile(r"log_(\d{1,6}) (\d{1,6})-log_(\d{1,6}) (\d{1,6})")   # log_2 32-log_2 4
_LOGPOWER_SOURCE = re.compile(r"log_(\d{1,6}) \((\d{1,6})\^(\d{1,6})\)")          # log_2 (4^3)
_NUMBER_TEXT = re.compile(r"(\d{1,6})(?:\.(\d{1,3}))?")                             # 5 or 2.5
_LOG_TEXT = re.compile(r"log_(\d{1,6}) (\d{1,6})")                                  # log_2 12

_CODES_BY_LAW = {
    "product": {"MULTIPLIED_EXPONENTS", "MULTIPLIED_BASES", "SUBTRACTED_EXPONENTS"},
    "quotient": {"ADDED_EXPONENTS", "DIVIDED_EXPONENTS", "DIVIDED_BASES"},
    "power": {"ADDED_EXPONENTS_POWER", "EXPONENT_AS_MULTIPLIER", "POWER_ONLY_ON_EXPONENT"},
    "tolog": {"LOG_BASE_AND_NUMBER_SWAPPED", "LOG_BASE_AND_RESULT_SWAPPED",
              "LOG_NUMBER_AND_RESULT_SWAPPED"},
    "toindex": {"INDEX_BASE_AND_EXPONENT_SWAPPED", "INDEX_BASE_AND_VALUE_SWAPPED",
                "INDEX_EXPONENT_AND_VALUE_SWAPPED"},
    "logvalue": {"DIVIDED_VALUE_BY_BASE", "SUBTRACTED_BASE_FROM_VALUE",
                 "COUNTED_MULTIPLICATION_SIGNS"},
    "logsum": {"LOG_OF_SUM", "MULTIPLIED_LOG_VALUES", "LOGS_IGNORED_NUMBERS_ADDED"},
    "logdiff": {"LOG_OF_DIFFERENCE", "DIVIDED_LOG_VALUES", "LOGS_IGNORED_NUMBERS_DIVIDED"},
    "logpower": {"LOG_RAISED_TO_POWER", "POWER_ADDED_TO_LOG", "POWER_IGNORED"},
}
_STATEMENT_LAWS = {"tolog", "toindex"}  # options are equations, not numbers
_LOG_LAWS = {"logvalue", "logsum", "logdiff", "logpower"}  # options are numbers or logs


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


def _power_equals(base: int, exponent: int, value: int) -> bool:
    """Is base^exponent == value? Stops early, so huge exponents cannot hang us."""
    if base == 1:
        return value == 1
    result = 1
    for _ in range(exponent):
        result *= base
        if result > value:
            return False
    return result == value


def _log_exact(base: int, number: int):
    """The whole number e with base^e == number, or None. Needs base >= 2."""
    if base < 2 or number < 1:
        raise ValueError("The base or the number of a logarithm is outside the allowed range.")
    result, exponent = 1, 0
    while result < number:
        result *= base
        exponent += 1
    return exponent if result == number else None


def _log_value(base: int, number: int):
    """A whole number when log_base(number) is whole, otherwise a tuple that names the log."""
    exponent = _log_exact(base, number)
    return Integer(exponent) if exponent is not None else ("log", base, number)


def _number_value(text: str):
    """Read '5', '2.5' or 'log_2 12' (no eval, no sympify)."""
    text = text.strip()
    match = _LOG_TEXT.fullmatch(text)
    if match:
        return _log_value(int(match[1]), int(match[2]))
    match = _NUMBER_TEXT.fullmatch(text)
    if match:
        if match[2] is None:
            return Integer(int(match[1]))
        return Rational(int(match[1] + match[2]), 10 ** len(match[2]))
    raise ValueError(f"Unreadable number: {text!r}")


def _statement_value(law: str, text: str) -> tuple:
    """Read 'log_2 32 = 5' (tolog) or '3^4 = 81' (toindex) into three numbers."""
    pattern = _LOG_STATEMENT if law == "tolog" else _INDEX_STATEMENT
    match = pattern.fullmatch(text.strip())
    if not match:
        raise ValueError(f"Unreadable statement: {text!r}")
    first, second, third = (int(g) for g in match.groups())
    if first < (2 if law == "tolog" else 1):
        raise ValueError("The base is outside the allowed range.")
    return first, second, third


def _statement_is_true(law: str, value: tuple) -> bool:
    first, second, third = value
    if law == "tolog":  # log_first second = third  means  first^third == second
        return _power_equals(first, third, second)
    return _power_equals(first, second, third)  # first^second = third


def _option_value(law: str, text: str):
    """One reader for every law: numbers for the first three, three-number tuples for the rest."""
    if law in _STATEMENT_LAWS:
        return _statement_value(law, text)
    if law in _LOG_LAWS:
        return _number_value(text)
    return _power_value(text)


def _power_value(text: str):
    """Read '2^7', '2^(7/2)' or '3 × 2^4' with strict patterns (no eval, no sympify)."""
    text = text.strip()
    match = _MULTIPLE.fullmatch(text)
    if match:
        factor = int(match[1])
        if not 1 <= factor <= MAX_BASE:
            raise ValueError(f"Factor {factor} is outside the allowed range.")
        return Integer(factor) * _checked_power(int(match[2]), int(match[3]))
    match = _POWER.fullmatch(text)
    if not match:
        raise ValueError(f"Unreadable power: {text!r}")
    base = int(match[1])
    if match[2] is not None:
        return _checked_power(base, int(match[2]))
    return _checked_power(base, int(match[3]), int(match[4]))


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
    match = _POWER_OF_POWER.fullmatch(text)
    if match:
        base, m, n = (int(g) for g in match.groups())
        if m > MAX_EXPONENT or n > MAX_EXPONENT:
            raise ValueError("Exponent is outside the allowed range.")
        return "power", base, m, n
    match = _TOLOG_SOURCE.fullmatch(text)
    if match:
        base, exponent, value = (int(g) for g in match.groups())
        if base < 2:
            raise ValueError("The base is outside the allowed range.")
        return "tolog", base, exponent, value
    match = _TOINDEX_SOURCE.fullmatch(text)
    if match:
        base, value, exponent = (int(g) for g in match.groups())
        if base < 2:
            raise ValueError("The base is outside the allowed range.")
        return "toindex", base, exponent, value
    match = _LOGSUM_SOURCE.fullmatch(text) or _LOGDIFF_SOURCE.fullmatch(text)
    if match:
        law = "logsum" if "+" in text else "logdiff"
        b1, big_m, b2, big_n = (int(g) for g in match.groups())
        if b1 != b2:
            raise ValueError("Both logarithms must have the same base.")
        i, j = _log_exact(b1, big_m), _log_exact(b1, big_n)
        if i is None or j is None:
            raise ValueError("Each number must be a whole power of the base.")
        if law == "logdiff" and i <= j:
            raise ValueError("The first number must be bigger than the second.")
        return law, b1, i, j
    match = _LOGPOWER_SOURCE.fullmatch(text)
    if match:
        base, inner, power = (int(g) for g in match.groups())
        k = _log_exact(base, inner)
        if k is None or k > MAX_EXPONENT or power > MAX_EXPONENT:
            raise ValueError("The question numbers are outside the allowed range.")
        return "logpower", base, k, power
    match = _LOGVALUE_SOURCE.fullmatch(text)
    if match:
        base, number = (int(g) for g in match.groups())
        exponent = _log_exact(base, number)
        if exponent is None:
            raise ValueError("The number must be a whole power of the base.")
        return "logvalue", base, exponent, number
    raise ValueError("Unknown question pattern.")


def _expected_value(source_expression: str):
    """Work out the true answer from the source expression."""
    law, base, m, n = _parse_source(source_expression)
    if law == "product":
        return _checked_power(base, m) * _checked_power(base, n)
    if law == "quotient":
        return _checked_power(base, m) / _checked_power(base, n)
    if law == "power":
        return _checked_power(base, m) ** n  # (base^m)^n
    if law == "logvalue":  # m = exponent
        return Integer(m)
    if law == "logsum":  # m = i, n = j
        return Integer(m + n)
    if law == "logdiff":
        return Integer(m - n)
    if law == "logpower":  # m = k, n = r
        return Integer(m * n)
    # tolog / toindex: m = exponent, n = value. The statement in the question must be true.
    if not _power_equals(base, m, n):
        raise ValueError("The statement in the question is false.")
    return (base, n, m) if law == "tolog" else (base, m, n)


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
    if code == "ADDED_EXPONENTS_POWER":
        return _checked_power(base, m + n)
    if code == "EXPONENT_AS_MULTIPLIER":
        return Integer(n) * _checked_power(base, m)
    if code == "POWER_ONLY_ON_EXPONENT":
        return _checked_power(base, m ** n)
    # log laws.  logvalue: m = exponent, n = number.  logsum/logdiff: m = i, n = j.  logpower: m = k, n = r
    if code == "DIVIDED_VALUE_BY_BASE":
        return Integer(n // base)
    if code == "SUBTRACTED_BASE_FROM_VALUE":
        return Integer(n - base)
    if code == "COUNTED_MULTIPLICATION_SIGNS":
        return Integer(m - 1)
    if code == "LOG_OF_SUM":
        return _log_value(base, base ** m + base ** n)
    if code == "MULTIPLIED_LOG_VALUES":
        return Integer(m * n)
    if code == "LOGS_IGNORED_NUMBERS_ADDED":
        return Integer(base ** m + base ** n)
    if code == "LOG_OF_DIFFERENCE":
        return _log_value(base, base ** m - base ** n)
    if code == "DIVIDED_LOG_VALUES":
        return Rational(m, n)
    if code == "LOGS_IGNORED_NUMBERS_DIVIDED":
        return Integer(base ** m // base ** n)
    if code == "LOG_RAISED_TO_POWER":
        return Integer(m ** n)
    if code == "POWER_ADDED_TO_LOG":
        return Integer(m + n)
    if code == "POWER_IGNORED":
        return Integer(m)
    # conversion laws: base, m = exponent, n = value
    if code == "LOG_BASE_AND_NUMBER_SWAPPED":
        return (n, base, m)
    if code == "LOG_BASE_AND_RESULT_SWAPPED":
        return (m, n, base)
    if code == "LOG_NUMBER_AND_RESULT_SWAPPED":
        return (base, m, n)
    if code == "INDEX_BASE_AND_EXPONENT_SWAPPED":
        return (m, base, n)
    if code == "INDEX_BASE_AND_VALUE_SWAPPED":
        return (n, m, base)
    if code == "INDEX_EXPONENT_AND_VALUE_SWAPPED":
        return (base, n, m)
    raise ValueError(f"Unknown misconception code: {code}")


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
    if _option_value(law, question.correct_expression) != expected:
        raise ValueError("correct_expression does not match the source expression.")

    values = []
    for option in options:
        value = _option_value(law, option.text)
        is_key = option.id == question.correct_option_id
        if is_key and option.misconception is not None:
            raise ValueError("The correct option must not have a misconception code.")
        if not is_key and not option.misconception:
            raise ValueError("Every wrong option needs a misconception code.")
        if is_key != (value == expected):
            raise ValueError("Key and distractor values do not match the true answer.")
        if law in _STATEMENT_LAWS and _statement_is_true(law, value) != is_key:
            raise ValueError("The key must be a true statement and every wrong option a false one.")
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
    "ADDED_EXPONENTS_POWER": "The exponents were added instead of multiplied in a power of a power.",
    "EXPONENT_AS_MULTIPLIER": "The outer exponent was treated as a multiplier instead of a power.",
    "POWER_ONLY_ON_EXPONENT": "Only the exponent was raised to the outer power; the base was left out.",
    "LOG_BASE_AND_NUMBER_SWAPPED": "The base and the number were swapped when writing the logarithm.",
    "LOG_BASE_AND_RESULT_SWAPPED": "The exponent was used as the base of the logarithm.",
    "LOG_NUMBER_AND_RESULT_SWAPPED": "The number and the answer of the logarithm were swapped.",
    "INDEX_BASE_AND_EXPONENT_SWAPPED": "The base and the exponent were swapped when writing the index form.",
    "INDEX_BASE_AND_VALUE_SWAPPED": "The number inside the logarithm was used as the base of the index form.",
    "INDEX_EXPONENT_AND_VALUE_SWAPPED": "The number inside the logarithm was used as the exponent.",
    "DIVIDED_VALUE_BY_BASE": "The number was divided by the base instead of finding the power.",
    "SUBTRACTED_BASE_FROM_VALUE": "The base was subtracted from the number instead of finding the power.",
    "COUNTED_MULTIPLICATION_SIGNS": "The multiplication signs were counted instead of the factors.",
    "LOG_OF_SUM": "The numbers were added inside one logarithm instead of adding the logarithms.",
    "MULTIPLIED_LOG_VALUES": "The values of the logarithms were multiplied instead of added.",
    "LOGS_IGNORED_NUMBERS_ADDED": "The logarithms were ignored and the numbers were added.",
    "LOG_OF_DIFFERENCE": "The numbers were subtracted inside one logarithm instead of subtracting the logarithms.",
    "DIVIDED_LOG_VALUES": "The values of the logarithms were divided instead of subtracted.",
    "LOGS_IGNORED_NUMBERS_DIVIDED": "The logarithms were ignored and the numbers were divided.",
    "LOG_RAISED_TO_POWER": "The logarithm was raised to the power instead of multiplying by the power.",
    "POWER_ADDED_TO_LOG": "The power was added to the logarithm instead of multiplying.",
    "POWER_IGNORED": "The power inside the logarithm was ignored.",
}

_FEEDBACK = {
    "MULTIPLIED_EXPONENTS": "You may have multiplied the exponents. When you MULTIPLY powers with the same base, you add the exponents.",
    "MULTIPLIED_BASES": "You may have multiplied the bases. The base stays the same; only the exponents change.",
    "SUBTRACTED_EXPONENTS": "You may have subtracted the exponents. Subtracting is for division, not for multiplication.",
    "ADDED_EXPONENTS": "You may have added the exponents. When you DIVIDE powers with the same base, you subtract the exponents.",
    "DIVIDED_EXPONENTS": "You may have divided the exponents. Divide the powers by subtracting the exponents.",
    "DIVIDED_BASES": "You may have divided the bases. The base stays the same; only the exponents change.",
    "ADDED_EXPONENTS_POWER": "You may have added the exponents. For a power of a power, you MULTIPLY the exponents.",
    "EXPONENT_AS_MULTIPLIER": "You may have used the outer exponent as 'times'. An exponent means repeated multiplication, so (a^m)^n means a^m multiplied by itself n times.",
    "POWER_ONLY_ON_EXPONENT": "You may have raised only the exponent to the outer power. The whole base power is raised, so the exponents are multiplied.",
    "LOG_BASE_AND_NUMBER_SWAPPED": "You may have swapped the base and the number. In log_b n, the base b is the same base as in the index form.",
    "LOG_BASE_AND_RESULT_SWAPPED": "You may have used the exponent as the base of the log. The base of the log is the base of the power.",
    "LOG_NUMBER_AND_RESULT_SWAPPED": "You may have swapped the number and the answer. The logarithm is the exponent, and the number is the value of the power.",
    "INDEX_BASE_AND_EXPONENT_SWAPPED": "You may have swapped the base and the exponent. The base of the log becomes the base of the power.",
    "INDEX_BASE_AND_VALUE_SWAPPED": "You may have used the number inside the log as the base. The number inside the log is the value of the power.",
    "INDEX_EXPONENT_AND_VALUE_SWAPPED": "You may have used the number inside the log as the exponent. The answer of the log is the exponent.",
    "DIVIDED_VALUE_BY_BASE": "You may have divided the number by the base. A log asks: which POWER of the base gives the number?",
    "SUBTRACTED_BASE_FROM_VALUE": "You may have subtracted the base from the number. A log asks: which POWER of the base gives the number?",
    "COUNTED_MULTIPLICATION_SIGNS": "You may have counted the multiplication signs. Count how many times the base is multiplied (the number of factors).",
    "LOG_OF_SUM": "You may have added the numbers inside one log. log a + log b = log (a x b); the numbers are multiplied, not added.",
    "MULTIPLIED_LOG_VALUES": "You may have multiplied the log values. The sum law says to ADD the logs of the same base.",
    "LOGS_IGNORED_NUMBERS_ADDED": "You may have dropped the logs and added the numbers. First find the value of each log, then add those values.",
    "LOG_OF_DIFFERENCE": "You may have subtracted the numbers inside one log. log a - log b = log (a / b); the numbers are divided, not subtracted.",
    "DIVIDED_LOG_VALUES": "You may have divided the log values. For a difference of logs, SUBTRACT the two log values.",
    "LOGS_IGNORED_NUMBERS_DIVIDED": "You may have dropped the logs and divided the numbers. First find the value of each log, then subtract those values.",
    "LOG_RAISED_TO_POWER": "You may have raised the log to the power. The power law is log (a^n) = n x log a: the power is a multiplier.",
    "POWER_ADDED_TO_LOG": "You may have added the power to the log. The power law says to MULTIPLY: log (a^n) = n x log a.",
    "POWER_IGNORED": "You may have ignored the power. The power comes down in front as a multiplier: log (a^n) = n x log a.",
}

_RECOMMENDATIONS = {
    "MULTIPLIED_EXPONENTS": "Expand a small example such as 2^2 x 2^3 as 2x2x2x2x2 to show why exponents are added, then practise the product law.",
    "MULTIPLIED_BASES": "Stress that the base is written once: show 2^2 x 2^3 = 2^5, then compare with (2x2)^5.",
    "SUBTRACTED_EXPONENTS": "Contrast the product law (add) and the quotient law (subtract) side by side with two short examples.",
    "ADDED_EXPONENTS": "Expand 6^5 / 6^2 as a fraction and cancel common factors to show the exponents are subtracted.",
    "DIVIDED_EXPONENTS": "Show that dividing powers cancels factors, so the exponents are subtracted, never divided.",
    "DIVIDED_BASES": "Cancel factors in a worked example: the base remains, only the number of factors changes.",
    "ADDED_EXPONENTS_POWER": "Write (2^3)^2 as 2^3 x 2^3 = 2^6 to show the exponents are multiplied, then contrast with the product law.",
    "EXPONENT_AS_MULTIPLIER": "Show that (2^3)^2 means 2^3 x 2^3, not 2 x 2^3. Practise writing the repeated multiplication.",
    "POWER_ONLY_ON_EXPONENT": "Expand (2^3)^2 fully as (2x2x2) x (2x2x2) and count the factors, to show the base is kept and the exponents are multiplied.",
    "LOG_BASE_AND_NUMBER_SWAPPED": "Use a colour code on 2^5 = 32: base, exponent, value. Then rewrite as log_2 32 = 5 keeping the colours: base stays base.",
    "LOG_BASE_AND_RESULT_SWAPPED": "Stress that the answer of a log is the exponent. Practise 'the log asks: what power of the base gives the number?'",
    "LOG_NUMBER_AND_RESULT_SWAPPED": "Read log_2 32 = 5 aloud as '2 to the power 5 gives 32', so the 32 is the value and the 5 is the exponent.",
    "INDEX_BASE_AND_EXPONENT_SWAPPED": "Use a colour code on log_3 81 = 4: the small base number stays the base of the power. Rewrite as 3^4 = 81.",
    "INDEX_BASE_AND_VALUE_SWAPPED": "Stress that the number inside the log is the value of the power (the big number), never the base.",
    "INDEX_EXPONENT_AND_VALUE_SWAPPED": "Stress that the answer of the log is the exponent. Read log_3 81 = 4 as '3 to the power 4 gives 81'.",
    "DIVIDED_VALUE_BY_BASE": "Ask 'which power of the base gives the number?' and practise with 2x2x2 = 8 so the answer is the number of 2s, not 8 / 2.",
    "SUBTRACTED_BASE_FROM_VALUE": "Build a small table of powers of 2 and 3 and read it backwards: 'which power gives 32?'",
    "COUNTED_MULTIPLICATION_SIGNS": "Write 2x2x2x2x2 and circle the factors, not the 'x' signs: five 2s means log_2 32 = 5.",
    "LOG_OF_SUM": "Show with numbers that log_2 4 + log_2 8 = 2 + 3 = 5 but log_2 (4 + 8) is not 5; the product law uses multiplication.",
    "MULTIPLIED_LOG_VALUES": "Evaluate each log first, then show that adding logs matches multiplying the numbers inside: log_2 4 + log_2 8 = log_2 32.",
    "LOGS_IGNORED_NUMBERS_ADDED": "Stress that 'log' is not decoration. Evaluate each log first (a whole number), then combine the values.",
    "LOG_OF_DIFFERENCE": "Show with numbers that log_2 32 - log_2 4 = 5 - 2 = 3 and equals log_2 (32 / 4) = log_2 8; subtraction becomes division inside the log.",
    "DIVIDED_LOG_VALUES": "Practise evaluating both logs and then subtracting; contrast the sum law (add) and the difference law (subtract).",
    "LOGS_IGNORED_NUMBERS_DIVIDED": "Stress that you cannot drop the logs. Evaluate each log first, then subtract the two values.",
    "LOG_RAISED_TO_POWER": "Expand log_2 (4^3) = log_2 (4 x 4 x 4) = log_2 4 + log_2 4 + log_2 4 = 3 x 2, to show the power becomes a multiplier.",
    "POWER_ADDED_TO_LOG": "Expand the power as repeated multiplication so students see 3 copies of log_2 4 are ADDED, which is multiplying by 3.",
    "POWER_IGNORED": "Practise the power law with small numbers and check each answer by evaluating the number inside the log first.",
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
