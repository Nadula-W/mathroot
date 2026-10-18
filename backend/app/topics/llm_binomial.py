
"""LLM question generation with automatic manual fallback."""

import json
import logging
import os
from urllib.request import Request, urlopen
from uuid import uuid4

from sympy import Symbol, expand, simplify

from app.contracts import InternalOption, InternalQuestion
from app.topics.binomial import BinomialTopic, _as_text

logger = logging.getLogger("uvicorn.error")
x = Symbol("x")

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3:4b-instruct"

SCHEMA = {
    "type": "object",
    "properties": {
        "outer": {"type": "integer"},
        "inner_x": {"type": "integer"},
        "constant": {"type": "integer"},
    },
    "required": ["outer", "inner_x", "constant"],
    "additionalProperties": False,
}


def generator_mode():
    value = os.getenv(
        "MATHROOT_GENERATOR", "auto"
    ).strip().lower()

    return value if value in {"auto", "manual"} else "auto"


def selected_model():
    return os.getenv(
        "MATHROOT_OLLAMA_MODEL", DEFAULT_MODEL
    ).strip() or DEFAULT_MODEL


def llm_status():
    result = {
        "mode": generator_mode(),
        "model": selected_model(),
        "available": False,
        "note": "Manual fallback is always available.",
    }

    if generator_mode() == "manual":
        result["note"] = "Manual mode selected."
        return result

    try:
        with urlopen(
            f"{OLLAMA_URL}/api/tags", timeout=2
        ) as response:
            models = json.load(response).get("models", [])

        result["available"] = any(
            item.get("name") == selected_model()
            or item.get("model") == selected_model()
            for item in models
        )

        result["note"] = (
            "Local LLM installed and available."
            if result["available"]
            else "Selected model not installed."
        )

    except (OSError, ValueError):
        result["note"] = (
            "Ollama unavailable. Manual fallback active."
        )

    return result


class LLMBinomialTopic(BinomialTopic):
    """
    Uses Ollama when available.
    Falls back to the original BinomialTopic otherwise.
    """

    def generate_question(
        self, difficulty: str
    ) -> InternalQuestion:

        if generator_mode() == "manual":
            logger.info("MathRoot: manual generator selected")
            return super().generate_question(difficulty)

        try:
            question = self._generate_using_ollama(difficulty)

            logger.info(
                "MathRoot: LLM question generated and verified"
            )
            return question

        except Exception as exc:
            logger.warning(
                "MathRoot: LLM failed (%s). Manual fallback.",
                exc,
            )
            return super().generate_question(difficulty)

    def _generate_using_ollama(
        self, difficulty: str
    ) -> InternalQuestion:

        if difficulty not in {"easy", "medium", "hard"}:
            raise ValueError("Unsupported difficulty")

        rules = {
            "easy": (
                "outer 2..6, inner_x 1..2, constant 2..9"
            ),
            "medium": (
                "outer 2..7, inner_x 1..4, constant -9..-2"
            ),
            "hard": (
                "outer -7..-2, inner_x 2..5, "
                "constant -9..-2 or 2..9"
            ),
        }

        seed = self.rng.randint(10000, 99999)

        prompt = (
            "Create ONE original Grade 10 Sri Lankan "
            "O/L Mathematics binomial expansion exercise. "
            "Use the expression format "
            "outer*(inner_x*x + constant). "
            f"Coefficient rules: {rules[difficulty]}. "
            f"Variation seed: {seed}. "
            "Use different numbers for different seeds. "
            "Return only JSON containing the integer fields "
            "outer, inner_x and constant. "
            "Do not provide answers or explanations."
        )

        payload = {
            "model": selected_model(),
            "stream": False,
            "format": SCHEMA,
            "options": {
                "temperature": 0.7,
                "num_predict": 100,
            },
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You create syllabus-aligned "
                        "Mathematics exercises."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        }

        request = Request(
            f"{OLLAMA_URL}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST",
        )

        with urlopen(request, timeout=60) as response:
            body = json.load(response)

        proposal = json.loads(
            body["message"]["content"]
        )

        values = (
            proposal.get("outer"),
            proposal.get("inner_x"),
            proposal.get("constant"),
        )

        if any(type(value) is not int for value in values):
            raise ValueError(
                "LLM returned invalid coefficients"
            )

        a, c, b = values

        valid = {
            "easy": (
                2 <= a <= 6
                and 1 <= c <= 2
                and 2 <= b <= 9
            ),
            "medium": (
                2 <= a <= 7
                and 1 <= c <= 4
                and -9 <= b <= -2
            ),
            "hard": (
                -7 <= a <= -2
                and 2 <= c <= 5
                and 2 <= abs(b) <= 9
            ),
        }

        if not valid[difficulty]:
            raise ValueError(
                "LLM coefficients outside allowed range"
            )

        # Calculate the answer independently.
        expected = expand(a * (c * x + b))

        # Correct answer + three diagnostic distractors.
        candidates = [
            (
                a * c * x + a * b,
                None,
            ),
            (
                a * c * x + b,
                "DISTRIBUTION_CONSTANT",
            ),
            (
                c * x + a * b,
                "DISTRIBUTION_VARIABLE",
            ),
            (
                a * c * x - a * b,
                "SIGN_ERROR",
            ),
        ]

        # Validate the correct option and all wrong options.
        for index, (expression, _) in enumerate(candidates):

            equivalent = (
                simplify(expression - expected) == 0
            )

            if equivalent != (index == 0):
                raise ValueError(
                    "Incorrect generated answer option"
                )

            for previous_expression, _ in candidates[:index]:
                if simplify(
                    expression - previous_expression
                ) == 0:
                    raise ValueError(
                        "Duplicate answer options"
                    )

        correct_id = str(uuid4())

        options = [
            InternalOption(
                id=(
                    correct_id
                    if label is None
                    else str(uuid4())
                ),
                text=_as_text(
                    int(expression.coeff(x)),
                    int(expression.subs(x, 0)),
                ),
                misconception=label,
            )
            for expression, label in candidates
        ]

        self.rng.shuffle(options)

        answer = _as_text(a * c, a * b)

        return InternalQuestion(
            id=str(uuid4()),
            topic_id=self.topic_id,
            difficulty=difficulty,
            statement=(
                f"Expand and simplify: "
                f"{a}({_as_text(c, b)})"
            ),
            options=options,
            correct_option_id=correct_id,
            explanation=(
                f"Multiply both terms by {a}. "
                f"{a} × ({_as_text(c, 0)}) "
                f"= {_as_text(a*c, 0)} and "
                f"{a} × ({b}) = {a*b}. "
                f"The answer is {answer}."
            ),
            source_expression=(
                f"({a})*(({c})*x+({b}))"
            ),
            correct_expression=str(expected),
        )
