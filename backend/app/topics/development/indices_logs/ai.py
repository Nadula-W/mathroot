"""Sadeepa: provider-specific code only. Choose any local or API-based model.

No provider is installed, contacted or selected by importing this placeholder.
"""
import os
import random
from uuid import uuid4

import httpx
from pydantic import BaseModel, Field

from app.answer_verification import Analysis, setting
from app.contracts import InternalOption, InternalQuestion
from . import manual

PREFIX = "MATHROOT_INDICES_LOGS"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"

# The AI call must always have a finite, sensible time limit (same rule as the shared verifier).
DEFAULT_TIMEOUT_SECONDS = 4.0
MIN_TIMEOUT_SECONDS = 0.1
MAX_TIMEOUT_SECONDS = 15.0


def configuration() -> dict:
    """Read this topic's backend environment; never print or commit credentials."""
    return {
        "mode": os.getenv(f"{PREFIX}_MODE", "auto").strip().lower(),
        "provider": os.getenv(f"{PREFIX}_PROVIDER", "").strip(),
        "model": os.getenv(f"{PREFIX}_MODEL", "").strip(),
        "base_url": os.getenv(f"{PREFIX}_BASE_URL", "").strip(),
        "api_key": os.getenv(f"{PREFIX}_API_KEY", ""),
        "timeout_seconds": setting(f"{PREFIX}_TIMEOUT_SECONDS",DEFAULT_TIMEOUT_SECONDS, MIN_TIMEOUT_SECONDS, MAX_TIMEOUT_SECONDS,),
    }


# ---------- The shape we ask the model to return ----------

class _AIOption(BaseModel):
    text: str
    misconception: str | None = None


class _AIOptions(BaseModel):
    options: list[_AIOption] = Field(min_length=4, max_length=4)


_SCHEMA = {
    "type": "object",
    "properties": {
        "options": {
            "type": "array",
            "minItems": 4,
            "maxItems": 4,
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "misconception": {"type": ["string", "null"]},
                },
                "required": ["text", "misconception"],
            },
        },
    },
    "required": ["options"],
}

_BASES = [2, 3, 5, 6]


def _pick_spec() -> tuple[str, int, int, int]:
    """OUR code chooses the law and the numbers. The model never does."""
    rng = random.SystemRandom()
    law = rng.choice(["product", "quotient", "power", "tolog", "toindex",
                      "logvalue", "logsum", "logdiff", "logpower"])
    if law in ("logvalue", "logsum", "logdiff", "logpower"):
        base, m, n = rng.choice(manual.log_specs(law))  # only specs with 4 different values
        return law, base, m, n
    if law in ("tolog", "toindex"):
        base, e = rng.choice(manual.conversion_specs(law))  # only specs with ONE true option
        return law, base, e, base ** e  # m = exponent, n = value
    if law == "power":
        base, m, n = rng.choice(manual.power_specs())  # only specs with 4 different values
        return law, base, m, n
    base = rng.choice(_BASES)
    if law == "product":
        # m != n, and skip (3, 6) / (6, 3): there two wrong options would be equal
        pairs = [(a, b) for a in range(2, 7) for b in range(2, 7)
                 if a != b and a * b != 2 * (a + b)]
        m, n = rng.choice(pairs)
    else:
        n = rng.randint(2, 4)
        m = rng.choice([k for k in range(n + 1, 9) if k % n != 0])
    return law, base, m, n


_EXAMPLES = {  # base 7 is never used in real questions, so it cannot be copied
    "product": (
        "Simplify: 7^5 × 7^3",
        '{"options": [{"text": "7^8", "misconception": null}, '
        '{"text": "7^15", "misconception": "MULTIPLIED_EXPONENTS"}, '
        '{"text": "49^8", "misconception": "MULTIPLIED_BASES"}, '
        '{"text": "7^2", "misconception": "SUBTRACTED_EXPONENTS"}]}',
    ),
    "quotient": (
        "Simplify: 7^7 ÷ 7^3",
        '{"options": [{"text": "7^4", "misconception": null}, '
        '{"text": "7^10", "misconception": "ADDED_EXPONENTS"}, '
        '{"text": "7^(7/3)", "misconception": "DIVIDED_EXPONENTS"}, '
        '{"text": "1^4", "misconception": "DIVIDED_BASES"}]}',
    ),
    "power": (
        "Simplify: (7^2)^3",
        '{"options": [{"text": "7^6", "misconception": null}, '
        '{"text": "7^5", "misconception": "ADDED_EXPONENTS_POWER"}, '
        '{"text": "3 × 7^2", "misconception": "EXPONENT_AS_MULTIPLIER"}, '
        '{"text": "7^8", "misconception": "POWER_ONLY_ON_EXPONENT"}]}',
    ),
    "tolog": (
        "Write 7^2 = 49 in logarithmic form.",
        '{"options": [{"text": "log_7 49 = 2", "misconception": null}, '
        '{"text": "log_49 7 = 2", "misconception": "LOG_BASE_AND_NUMBER_SWAPPED"}, '
        '{"text": "log_2 49 = 7", "misconception": "LOG_BASE_AND_RESULT_SWAPPED"}, '
        '{"text": "log_7 2 = 49", "misconception": "LOG_NUMBER_AND_RESULT_SWAPPED"}]}',
    ),
    "toindex": (
        "Write log_7 49 = 2 in index form.",
        '{"options": [{"text": "7^2 = 49", "misconception": null}, '
        '{"text": "2^7 = 49", "misconception": "INDEX_BASE_AND_EXPONENT_SWAPPED"}, '
        '{"text": "49^2 = 7", "misconception": "INDEX_BASE_AND_VALUE_SWAPPED"}, '
        '{"text": "7^49 = 2", "misconception": "INDEX_EXPONENT_AND_VALUE_SWAPPED"}]}',
    ),
    "logvalue": (
        "Find the value of log_7 343.",
        '{"options": [{"text": "3", "misconception": null}, '
        '{"text": "49", "misconception": "DIVIDED_VALUE_BY_BASE"}, '
        '{"text": "336", "misconception": "SUBTRACTED_BASE_FROM_VALUE"}, '
        '{"text": "2", "misconception": "COUNTED_MULTIPLICATION_SIGNS"}]}',
    ),
    "logsum": (
        "Find the value of log_7 49 + log_7 343.",
        '{"options": [{"text": "5", "misconception": null}, '
        '{"text": "log_7 392", "misconception": "LOG_OF_SUM"}, '
        '{"text": "6", "misconception": "MULTIPLIED_LOG_VALUES"}, '
        '{"text": "392", "misconception": "LOGS_IGNORED_NUMBERS_ADDED"}]}',
    ),
    "logdiff": (
        "Find the value of log_7 16807 - log_7 49.",
        '{"options": [{"text": "3", "misconception": null}, '
        '{"text": "log_7 16758", "misconception": "LOG_OF_DIFFERENCE"}, '
        '{"text": "2.5", "misconception": "DIVIDED_LOG_VALUES"}, '
        '{"text": "343", "misconception": "LOGS_IGNORED_NUMBERS_DIVIDED"}]}',
    ),
    "logpower": (
        "Find the value of log_7 (49^3).",
        '{"options": [{"text": "6", "misconception": null}, '
        '{"text": "8", "misconception": "LOG_RAISED_TO_POWER"}, '
        '{"text": "5", "misconception": "POWER_ADDED_TO_LOG"}, '
        '{"text": "2", "misconception": "POWER_IGNORED"}]}',
    ),
}


_FORMAT_RULE = {
    "product": 'is ONLY a power like 3^6 (or a product like 3 × 2^4 when the mistake says so)',
    "quotient": 'is ONLY a power like 3^6 (or a power like 6^(5/2) when the mistake says so)',
    "power": 'is ONLY a power like 3^6 (or a product like 3 × 2^4 when the mistake says so)',
    "tolog": 'is ONLY an equation written exactly like log_3 81 = 4 (log_, the base, a space, the number, " = ", the answer)',
    "toindex": 'is ONLY an equation written exactly like 3^4 = 81',
    "logvalue": 'is ONLY a whole number like 5',
    "logsum": 'is ONLY a whole number like 5, or a logarithm written exactly like log_2 12 when the mistake says so',
    "logdiff": 'is ONLY a whole number like 3, a decimal like 2.5, or a logarithm written exactly like log_2 28 when the mistake says so',
    "logpower": 'is ONLY a whole number like 6',
}


def _mistakes(law: str, base: int, m: int, n: int) -> tuple[str, str]:
    """(how to get the correct answer, the 3 mistakes with this question's numbers)"""
    if law == "product":
        return (
            f"add the exponents ({m} + {n}) and keep the base {base}",
            f"  MULTIPLIED_EXPONENTS: the student multiplies the exponents ({m} × {n}) and keeps the base {base}\n"
            f"  MULTIPLIED_BASES: the student adds the exponents ({m} + {n}) but also multiplies the bases "
            f"({base} × {base} = {base * base}), so the base becomes {base * base}\n"
            f"  SUBTRACTED_EXPONENTS: the student subtracts the exponents (bigger minus smaller) and keeps the base {base}",
        )
    if law == "logvalue":  # m = exponent, n = number
        return (
            f"count how many times {base} is multiplied to make {n}",
            f"  DIVIDED_VALUE_BY_BASE: the student divides the number {n} by the base {base}\n"
            f"  SUBTRACTED_BASE_FROM_VALUE: the student subtracts the base {base} from the number {n}\n"
            f"  COUNTED_MULTIPLICATION_SIGNS: the student counts the multiplication signs instead of the "
            f"factors, so the answer is one less than the correct one",
        )
    if law in ("logsum", "logdiff"):  # m = i, n = j
        big_m, big_n = base ** m, base ** n
        if law == "logsum":
            return (
                f"find log_{base} {big_m} and log_{base} {big_n}, then add the two values",
                f"  LOG_OF_SUM: the student adds the numbers inside one log: write log_{base} {big_m + big_n}\n"
                f"  MULTIPLIED_LOG_VALUES: the student multiplies the two log values ({m} × {n}) instead of adding\n"
                f"  LOGS_IGNORED_NUMBERS_ADDED: the student drops the logs and just adds {big_m} + {big_n}",
            )
        return (
            f"find log_{base} {big_m} and log_{base} {big_n}, then subtract the second value from the first",
            f"  LOG_OF_DIFFERENCE: the student subtracts the numbers inside one log: write log_{base} {big_m - big_n}\n"
            f"  DIVIDED_LOG_VALUES: the student divides the first log value by the second ({m} ÷ {n}); "
            f"write it as a decimal like 2.5\n"
            f"  LOGS_IGNORED_NUMBERS_DIVIDED: the student drops the logs and just divides {big_m} ÷ {big_n}",
        )
    if law == "logpower":  # m = k, n = r
        inner = base ** m
        return (
            f"multiply the power {n} by log_{base} {inner} (which is {m})",
            f"  LOG_RAISED_TO_POWER: the student raises the log value {m} to the power {n}\n"
            f"  POWER_ADDED_TO_LOG: the student adds the power {n} to the log value {m}\n"
            f"  POWER_IGNORED: the student ignores the power {n} and gives log_{base} {inner}",
        )
    if law == "tolog":  # m = exponent, n = value
        return (
            f"the base {base} stays the base of the log, the number is {n}, the answer is the exponent {m}",
            f"  LOG_BASE_AND_NUMBER_SWAPPED: the student swaps the base {base} and the number {n}\n"
            f"  LOG_BASE_AND_RESULT_SWAPPED: the student swaps the base {base} and the answer {m}\n"
            f"  LOG_NUMBER_AND_RESULT_SWAPPED: the student swaps the number {n} and the answer {m}",
        )
    if law == "toindex":
        return (
            f"the base {base} of the log is the base of the power, the answer {m} is the exponent, "
            f"and {n} is the value",
            f"  INDEX_BASE_AND_EXPONENT_SWAPPED: the student swaps the base {base} and the exponent {m}\n"
            f"  INDEX_BASE_AND_VALUE_SWAPPED: the student swaps the base {base} and the value {n}\n"
            f"  INDEX_EXPONENT_AND_VALUE_SWAPPED: the student swaps the exponent {m} and the value {n}",
        )
    if law == "power":
        return (
            f"multiply the exponents ({m} × {n}) and keep the base {base}",
            f"  ADDED_EXPONENTS_POWER: the student adds the exponents ({m} + {n}) and keeps the base {base}\n"
            f"  EXPONENT_AS_MULTIPLIER: the student reads the outer exponent as \"times\": write it as {n} × {base}^{m}\n"
            f"  POWER_ONLY_ON_EXPONENT: the student raises only the exponent {m} to the power {n} "
            f"({m}^{n} = {m ** n}) and keeps the base {base}: {base}^{m ** n}",
        )
    return (
        f"subtract the exponents ({m} - {n}) and keep the base {base}",
        f"  ADDED_EXPONENTS: the student adds the exponents ({m} + {n}) and keeps the base {base}\n"
        f"  DIVIDED_EXPONENTS: the student divides the exponents ({m} ÷ {n}) and keeps the base {base}; "
        f"write it as {base}^({m}/{n})\n"
        f"  DIVIDED_BASES: the student divides the bases ({base} ÷ {base} = 1), so the base becomes 1, "
        f"and subtracts the exponents: 1^{m - n}",
    )


def _build_prompt(law: str, base: int, m: int, n: int, difficulty: str) -> str:
    correct_rule, mistakes = _mistakes(law, base, m, n)
    example_question, example_json = _EXAMPLES[law]
    statement, _ = manual.question_texts(law, base, m, n)
    return (
        "You are helping to write a Grade 10 (Sri Lankan O/L) mathematics multiple-choice question.\n"
        f"The question is already fixed: {statement}\n"
        "Write only the 4 answer options.\n"
        "Rules:\n"
        f"- Each option \"text\" {_FORMAT_RULE[law]}. No other words.\n"
        f"- Exactly one option is correct ({correct_rule}). Its \"misconception\" is null.\n"
        "- The other 3 options are wrong answers. Use each of these codes exactly once:\n"
        f"{mistakes}\n"
        "- Work out each number carefully.\n"
        "Example of the format only (different numbers):\n"
        f"Question: {example_question}\n"
        f"{example_json}\n"
        "Return only JSON like the example."
    )


# ---------- Talking to the model ----------

def _call_ollama(prompt: str, cfg: dict) -> str:
    """Send the prompt to a local Ollama server and return the raw JSON text."""
    base_url = cfg["base_url"] or DEFAULT_OLLAMA_URL
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": _SCHEMA,
        "options": {"temperature": 0.2, "num_predict": 200},
    }
    response = httpx.post(
        f"{base_url}/api/chat", json=payload, timeout=float(cfg["timeout_seconds"])
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def _to_question(raw_text: str, spec: tuple, difficulty: str) -> InternalQuestion:
    """Turn the model's options into an InternalQuestion. Raises on anything odd."""
    law, base, m, n = spec
    data = _AIOptions.model_validate_json(raw_text)

    correct = [o for o in data.options if o.misconception is None]
    if len(correct) != 1:
        raise ValueError("Exactly one option must be correct.")

    # Statement, source expression and explanation are ALL written by our code.
    statement, source = manual.question_texts(law, base, m, n)

    identified = [(str(uuid4()), o.text.strip(), o.misconception) for o in data.options]
    random.SystemRandom().shuffle(identified)
    correct_id = next(i for i, _, code in identified if code is None)
    options = [InternalOption(id=i, text=t, misconception=c) for i, t, c in identified]

    return InternalQuestion(
        id=str(uuid4()),
        topic_id=manual.TOPIC_ID,
        difficulty=difficulty,
        statement=statement,
        options=options,
        correct_option_id=correct_id,
        explanation=manual.explain(source),
        source_expression=source,
        correct_expression=correct[0].text.strip(),
    )


def generate_question(difficulty: str) -> InternalQuestion:
    cfg = configuration()
    if not cfg["model"]:
        raise RuntimeError("No model is configured for indices_logs.")
    if cfg["provider"] not in ("", "ollama"):
        raise RuntimeError("Unsupported provider.")
    spec = _pick_spec()
    law, base, m, n = spec
    raw_text = _call_ollama(_build_prompt(law, base, m, n, difficulty), cfg)
    return _to_question(raw_text, spec, difficulty)


def analyze_answer(context: dict) -> Analysis:
    # TODO: Call your chosen provider using the mathematical context supplied
    # by the shared verifier, with a finite timeout and structured JSON output.
    # Return Analysis.model_validate_json(response_text), or convert validated
    # provider fields into Analysis. Do not copy the shared grading/fallback logic.
    # proposed_correct must agree with context['verified_correct']; diagnoses
    # must match context['supported_misconception'] (or None when unknown).
    # explanation and corrective_guidance must be selected verbatim from
    # context['approved_explanations'] and context['approved_guidance'].
    # The shared service checks confidence and rejects unsupported output.
    raise NotImplementedError("Choose and implement indices_logs AI answer analysis.")


class TopicFeedbackProvider:
    """Structural implementation of the existing FeedbackProvider interface."""
    def analyze(self, context: dict) -> Analysis:
        if configuration()["mode"] == "manual":
            # Caught by the shared service; no network request is made.
            raise RuntimeError("Topic configured for manual feedback.")
        return analyze_answer(context)


class TopicTranslationProvider:
    """Optional Sinhala translation using this topic's provider configuration."""
    def translate(self, text: str) -> str:
        # TODO: Read configuration() and translate the masked prose to Sinhala.
        # Preserve each [[MATH_n]] placeholder exactly once in the same order.
        # Return the translated string, with a finite network timeout. Do not
        # translate or solve the hidden mathematics and do not send identities.
        # You may use Ollama, Gemini, OpenRouter, another API, or remain manual.
        # The shared presentation service additionally requires this topic's
        # validate_translation hook to approve the meaning before display.
        if configuration()["mode"] == "manual":
            raise RuntimeError("Topic configured for manual translation.")
        raise NotImplementedError("Choose and implement this topic's translation provider.")
