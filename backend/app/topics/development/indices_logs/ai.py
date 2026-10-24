"""Sadeepa: provider-specific code only. Choose any local or API-based model.

No provider is installed, contacted or selected by importing this placeholder.
"""
import os

from app.answer_verification import Analysis
from app.contracts import InternalQuestion

PREFIX = "MATHROOT_INDICES_LOGS"


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


def generate_question(difficulty: str) -> InternalQuestion:
    # TODO: Read configuration(), call your chosen provider with a finite timeout,
    # validate its structured JSON, and convert it to InternalQuestion.
    # Gemini, OpenRouter, Ollama and other providers are all valid choices.
    # Use the existing httpx dependency if useful; add no SDK unless needed.
    # Do not send identities, sessions or database credentials to the provider.
    # Raise on unavailable services, timeouts, missing config or malformed data.
    # generator.py automatically tries manual.generate_question on failure.
    raise NotImplementedError("Choose and implement indices_logs AI generation.")


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
