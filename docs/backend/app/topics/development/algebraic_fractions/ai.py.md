# ai.py — code explained

**Source:** [backend/app/topics/development/algebraic_fractions/ai.py](../../../../../../backend/app/topics/development/algebraic_fractions/ai.py) · [All backend explanations](../../../../SOURCE_INDEX.md)

**What and how:** algebraic_fractions: Contains this member's independent provider settings and AI-call TODOs. This starter is unregistered and unfinished; explicit NotImplementedError is intentional.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.



**Bilingual update:** The existing member-owned configuration and analysis TODOs remain. TopicTranslationProvider is an optional masked-prose adapter TODO using the same independent provider settings; manual mode prevents calls, and topic semantic approval is still required.

## Lines 1–11: Code section

```python
"""Fernando: provider-specific code only. Choose any local or API-based model.

No provider is installed, contacted or selected by importing this placeholder.
"""
import os

from app.answer_verification import Analysis
from app.contracts import InternalQuestion

PREFIX = "MATHROOT_ALGEBRAIC_FRACTIONS"

```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 13–23: configuration

```python
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

```

**Explanation:**

- Reads this member's own provider/model/endpoint/key/mode environment prefix. Timeout remains a string until the member implements parsing and bounded HTTP calls.
- Reads environment settings instead of committing API keys/provider choices to source.

## Lines 25–34: generate_question

```python
def generate_question(difficulty: str) -> InternalQuestion:
    # TODO: Read configuration(), call your chosen provider with a finite timeout,
    # validate its structured JSON, and convert it to InternalQuestion.
    # Gemini, OpenRouter, Ollama and other providers are all valid choices.
    # Use the existing httpx dependency if useful; add no SDK unless needed.
    # Do not send identities, sessions or database credentials to the provider.
    # Raise on unavailable services, timeouts, missing config or malformed data.
    # generator.py automatically tries manual.generate_question on failure.
    raise NotImplementedError("Choose and implement algebraic_fractions AI generation.")

```

**Explanation:**

- In ai.py/manual.py this is an unfinished topic TODO. In generator.py it validates difficulty, tries AI plus mathematical validation, and falls back to the manual generator. The adapter class delegates to the same module-level function.
- This is a deliberate unfinished TODO. The topic/provider is not a completed mathematics implementation.

## Lines 36–47: analyze_answer

```python
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
    raise NotImplementedError("Choose and implement algebraic_fractions AI answer analysis.")

```

**Explanation:**

- An explicit member TODO that must return validated grounded Analysis. NotImplementedError means this provider is not implemented yet.
- Checks the returned JSON/object against Pydantic before using its fields.
- This is a deliberate unfinished TODO. The topic/provider is not a completed mathematics implementation.

## Lines 49–50: TopicFeedbackProvider

```python
class TopicFeedbackProvider:
    """Structural implementation of the existing FeedbackProvider interface."""
```

**Explanation:**

- Groups the fields/methods of TopicFeedbackProvider. Declarations alone do not call a model or create database records; the following method sections explain execution.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 51–70: analyze()

```python
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
```

**Explanation:**

- Checks the topic's manual mode and otherwise delegates to analyze_answer. Raised errors are caught by the existing shared verifier for manual fallback.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Connected files

Follow these imports to their matching code explanations:

- [app/answer_verification.py](../../../answer_verification.py.md)
- [app/contracts.py](../../../contracts.py.md)

## How to explain this file in the viva

“algebraic_fractions: Contains this member's independent provider settings and AI-call TODOs. This starter is unregistered and unfinished; explicit NotImplementedError is intentional.”
