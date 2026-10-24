# generator.py — code explained

**Source:** [backend/app/topics/development/binomial/generator.py](../../../../../../backend/app/topics/development/binomial/generator.py) · [All backend explanations](../../../../SOURCE_INDEX.md)

**What and how:** Working Ollama question generator extending BinomialTopic. It requests coefficients, independently computes/checks mathematics and falls back to the manual generator.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–19: Code section

```python
"""LLM question generation with automatic manual fallback."""

import json
import logging
import os
from urllib.request import Request, urlopen
from uuid import uuid4

from sympy import Symbol, expand, simplify

from app.contracts import InternalOption, InternalQuestion
from .manual import BinomialTopic, _as_text

logger = logging.getLogger("uvicorn.error")
x = Symbol("x")

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3:4b-instruct"
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 21–30: Code section

```python
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
```

**Explanation:**

- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 33–38: generator_mode()

```python
def generator_mode():
    value = os.getenv(
        "MATHROOT_GENERATOR", "auto"
    ).strip().lower()

    return value if value in {"auto", "manual"} else "auto"
```

**Explanation:**

- Reads MATHROOT_GENERATOR, accepting auto/manual and defaulting unknown modes to auto.
- Reads environment settings instead of committing API keys/provider choices to source.

## Lines 41–44: selected_model()

```python
def selected_model():
    return os.getenv(
        "MATHROOT_OLLAMA_MODEL", DEFAULT_MODEL
    ).strip() or DEFAULT_MODEL
```

**Explanation:**

- Reads MATHROOT_OLLAMA_MODEL or uses the existing default local model name.
- Reads environment settings instead of committing API keys/provider choices to source.

## Lines 47–69: llm_status()

```python
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
```

**Explanation:**

- Checks the local Ollama model list with a short timeout and reports whether manual fallback is active.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 71–82: llm_status()

```python
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
```

**Explanation:**

- Checks the local Ollama model list with a short timeout and reports whether manual fallback is active.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 85–89: LLMBinomialTopic

```python
class LLMBinomialTopic(BinomialTopic):
    """
    Uses Ollama when available.
    Falls back to the original BinomialTopic otherwise.
    """
```

**Explanation:**

- Groups the fields/methods of LLMBinomialTopic. Declarations alone do not call a model or create database records; the following method sections explain execution.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 91–112: generate_question()

```python
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
```

**Explanation:**

- Manual mode uses the parent rule-based generator. Auto mode tries _generate_using_ollama and catches errors so a valid manual question is returned instead.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.

## Lines 114–134: _generate_using_ollama()

```python
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
```

**Explanation:**

- Requests coefficients under difficulty constraints, validates types/ranges and independently computes the answer with SymPy. It builds diagnostic options, checks mathematical uniqueness and assigns opaque UUIDs.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 136–147: _generate_using_ollama()

```python
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
```

**Explanation:**

- Requests coefficients under difficulty constraints, validates types/ranges and independently computes the answer with SymPy. It builds diagnostic options, checks mathematical uniqueness and assigns opaque UUIDs.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 149–170: _generate_using_ollama()

```python
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
```

**Explanation:**

- Requests coefficients under difficulty constraints, validates types/ranges and independently computes the answer with SymPy. It builds diagnostic options, checks mathematical uniqueness and assigns opaque UUIDs.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 172–197: _generate_using_ollama()

```python
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
```

**Explanation:**

- Requests coefficients under difficulty constraints, validates types/ranges and independently computes the answer with SymPy. It builds diagnostic options, checks mathematical uniqueness and assigns opaque UUIDs.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 199–222: _generate_using_ollama()

```python
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
```

**Explanation:**

- Requests coefficients under difficulty constraints, validates types/ranges and independently computes the answer with SymPy. It builds diagnostic options, checks mathematical uniqueness and assigns opaque UUIDs.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 224–248: _generate_using_ollama()

```python
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
```

**Explanation:**

- Requests coefficients under difficulty constraints, validates types/ranges and independently computes the answer with SymPy. It builds diagnostic options, checks mathematical uniqueness and assigns opaque UUIDs.
- Uses SymPy to expand the expression independently of the LLM.
- Line 225: Computes the expected result independently with SymPy instead of trusting an LLM-generated answer string.

## Lines 250–267: _generate_using_ollama()

```python
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
```

**Explanation:**

- Requests coefficients under difficulty constraints, validates types/ranges and independently computes the answer with SymPy. It builds diagnostic options, checks mathematical uniqueness and assigns opaque UUIDs.
- Creates opaque IDs so option identifiers do not reveal correctness/misconception semantics.
- Checks symbolic mathematical equivalence rather than matching display text.
- Line 254: Requires the first candidate to be mathematically correct and every distractor to be mathematically wrong.

## Lines 269–287: _generate_using_ollama()

```python
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
```

**Explanation:**

- Requests coefficients under difficulty constraints, validates types/ranges and independently computes the answer with SymPy. It builds diagnostic options, checks mathematical uniqueness and assigns opaque UUIDs.
- Creates opaque IDs so option identifiers do not reveal correctness/misconception semantics.

## Lines 289–310: _generate_using_ollama()

```python
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
```

**Explanation:**

- Requests coefficients under difficulty constraints, validates types/ranges and independently computes the answer with SymPy. It builds diagnostic options, checks mathematical uniqueness and assigns opaque UUIDs.
- Creates opaque IDs so option identifiers do not reveal correctness/misconception semantics.

## Connected files

Follow these imports to their matching code explanations:

- [app/contracts.py](../../../contracts.py.md)
- [app/topics/development/binomial/manual.py](manual.py.md)

## How to explain this file in the viva

“Working Ollama question generator extending BinomialTopic. It requests coefficients, independently computes/checks mathematics and falls back to the manual generator.”
