"""Sadeepa: provider-specific code only. Choose any local or API-based model.

No provider is installed, contacted or selected by importing this placeholder.
"""
import os
import random
from uuid import uuid4

import httpx
from pydantic import BaseModel, Field

from app.answer_verification import Analysis
from app.contracts import InternalOption, InternalQuestion
from . import manual

PREFIX = "MATHROOT_INDICES_LOGS"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"


def configuration() -> dict:
    """Read this topic's backend environment; never print or commit credentials."""
    return {
        "mode": os.getenv(f"{PREFIX}_MODE", "auto").strip().lower(),
        "provider": os.getenv(f"{PREFIX}_PROVIDER", "").strip(),
        "model": os.getenv(f"{PREFIX}_MODEL", "").strip(),
        "base_url": os.getenv(f"{PREFIX}_BASE_URL", "").strip(),
        "api_key": os.getenv(f"{PREFIX}_API_KEY", ""),
        "timeout_seconds": os.getenv(f"{PREFIX}_TIMEOUT_SECONDS", "4"),
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
_OPERATOR = {"product": "×", "quotient": "÷"}


def _pick_spec() -> tuple[str, int, int, int]:
    """OUR code chooses the law and the numbers. The model never does."""
    rng = random.SystemRandom()
    law = rng.choice(["product", "quotient"])
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
    return (
        "You are helping to write a Grade 10 (Sri Lankan O/L) mathematics multiple-choice question.\n"
        f"The question is already fixed: Simplify: {base}^{m} {_OPERATOR[law]} {base}^{n}\n"
        "Write only the 4 answer options.\n"
        "Rules:\n"
        "- Each option \"text\" is ONLY a power, like 3^6. No words, no \"=\", no letters.\n"
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
    operator = _OPERATOR[law]
    source = f"{base}^{m}*{base}^{n}" if law == "product" else f"{base}^{m}/{base}^{n}"

    identified = [(str(uuid4()), o.text.strip(), o.misconception) for o in data.options]
    random.SystemRandom().shuffle(identified)
    correct_id = next(i for i, _, code in identified if code is None)
    options = [InternalOption(id=i, text=t, misconception=c) for i, t, c in identified]

    return InternalQuestion(
        id=str(uuid4()),
        topic_id=manual.TOPIC_ID,
        difficulty=difficulty,
        statement=f"Simplify: {base}^{m} {operator} {base}^{n}",
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
