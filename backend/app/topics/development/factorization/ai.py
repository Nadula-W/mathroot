"""Bopage: provider-specific code for factorization AI generation and feedback."""
import json
import os
import random
from uuid import uuid4

import httpx
from pydantic import BaseModel, ConfigDict, Field, StrictBool

from app.answer_verification import Analysis
from app.contracts import InternalOption, InternalQuestion
from . import manual

PREFIX = "MATHROOT_FACTORIZATION"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"


def configuration() -> dict:
    """Read this topic's backend environment; never print or commit credentials."""
    return {
        "mode": os.getenv(f"{PREFIX}_MODE", "auto").strip().lower(),
        "provider": os.getenv(f"{PREFIX}_PROVIDER", "").strip().lower(),
        "model": os.getenv(f"{PREFIX}_MODEL", "").strip(),
        "base_url": os.getenv(f"{PREFIX}_BASE_URL", DEFAULT_OLLAMA_URL).strip(),
        "api_key": os.getenv(f"{PREFIX}_API_KEY", ""),
        "timeout_seconds": os.getenv(f"{PREFIX}_TIMEOUT_SECONDS", "4").strip(),
    }


class _AIOption(BaseModel):
    text: str
    misconception: str | None = None


class _AIOptions(BaseModel):
    options: list[_AIOption] = Field(min_length=4, max_length=4)


class FeedbackSelection(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    proposed_correct: StrictBool
    explanation_index: int = Field(ge=0)
    suspected_misconception: str | None
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    guidance_index: int = Field(ge=0)


def _timeout(cfg: dict) -> float:
    try:
        val = float(cfg.get("timeout_seconds", 4))
        return val if 0.1 <= val <= 15.0 else 4.0
    except ValueError:
        return 4.0


def _call_ollama(prompt: str, cfg: dict) -> str:
    base_url = cfg["base_url"] or DEFAULT_OLLAMA_URL
    payload = {
        "model": cfg["model"],
        "stream": False,
        "format": "json",
        "think": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a mathematics question generator for secondary school quadratic factorization. "
                    "Output JSON ONLY matching: {\"options\": [{\"text\": \"(x + a)(x + b)\", \"misconception\": null or string}]}. "
                    "Exactly one option must have misconception null (the correct factorization). "
                    "All other options must have one of these misconception codes: "
                    f"{list(manual.MISCONCEPTIONS.keys())}."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "options": {"temperature": 0.1, "num_predict": 250},
    }
    with httpx.Client(timeout=_timeout(cfg), http2=False) as client:
        response = client.post(f"{base_url}/api/chat", json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]


def _pick_spec(difficulty: str) -> tuple[int, int, int, str]:
    """Pick quadratic coefficients (a, b, c, expected_factors). OUR code chooses the math."""
    rng = random.SystemRandom()
    if difficulty == "easy":
        d = rng.choice([2, 3, 4, 5])
        return 1, 0, -(d * d), f"(x - {d})(x + {d})"
    if difficulty == "medium":
        candidates = [(4, 2), (5, 2), (6, 3), (5, 3), (4, 3)]
        p, q = rng.choice(candidates)
        return 1, p - q, -(p * q), f"(x + {p})(x - {q})"
    # hard
    a, p, q = 2, 1, 3
    return a, a * q + p, p * q, f"({a}x + {p})(x + {q})"


def _build_prompt(difficulty: str) -> tuple[str, str, str, str]:
    a, b, c, expected_factors = _pick_spec(difficulty)
    quad_str = manual._format_quadratic(a, b, c)
    statement = f"Factorize: {quad_str}"
    source = f"{a}*x**2 + ({b})*x + ({c})" if b != 0 else f"{a}*x**2 + ({c})"
    expl = f"The factors are {expected_factors}."
    prompt = (
        f"Generate 4 multiple choice options for: {statement}\n"
        f"Correct factorization: {expected_factors}\n"
        "Return valid JSON with 4 options. Distractors must test SIGN_ERROR, WRONG_FACTOR_PAIR, "
        "SUM_PRODUCT_CONFUSION, or COEFFICIENT_FACTOR_MISALLOCATION."
    )
    return prompt, statement, source, expl


def _to_question(raw_text: str, statement: str, source: str, expl: str, difficulty: str) -> InternalQuestion:
    data = _AIOptions.model_validate_json(raw_text)
    correct = [o for o in data.options if o.misconception is None]
    if len(correct) != 1:
        raise ValueError("Exactly one option must be correct.")

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
        explanation=expl,
        source_expression=source,
        correct_expression=correct[0].text.strip(),
    )


def generate_question(difficulty: str) -> InternalQuestion:
    cfg = configuration()
    if cfg["mode"] == "manual":
        raise RuntimeError("Topic configured for manual mode.")
    if not cfg["model"]:
        raise RuntimeError("No model is configured for factorization.")
    if cfg["provider"] not in ("", "ollama"):
        raise RuntimeError(f"Unsupported provider: {cfg['provider']}")

    prompt, statement, source, expl = _build_prompt(difficulty)
    raw_text = _call_ollama(prompt, cfg)
    return _to_question(raw_text, statement, source, expl, difficulty)


def analyze_answer(context: dict) -> Analysis:
    cfg = configuration()
    if cfg["mode"] == "manual":
        raise RuntimeError("Topic configured for manual feedback.")
    if not cfg["model"]:
        raise RuntimeError("No model is configured for factorization.")

    base_url = cfg["base_url"] or DEFAULT_OLLAMA_URL
    payload = {
        "model": cfg["model"],
        "stream": False,
        "format": FeedbackSelection.model_json_schema(),
        "think": False,
        "options": {"temperature": 0, "num_predict": 180},
        "messages": [
            {
                "role": "system",
                "content": (
                    "Analyze this multiple-choice quadratic factorization response. "
                    "The verified grade and diagnostic evidence are authoritative. Return JSON schema only. "
                    "Select explanation_index and guidance_index as zero-based indices into approved_explanations and approved_guidance."
                ),
            },
            {"role": "user", "content": json.dumps(context)},
        ],
    }
    with httpx.Client(timeout=_timeout(cfg), http2=False) as client:
        response = client.post(f"{base_url}/api/chat", json=payload)
        response.raise_for_status()
        selection = FeedbackSelection.model_validate_json(response.json()["message"]["content"])
        return Analysis(
            proposed_correct=selection.proposed_correct,
            explanation=context["approved_explanations"][selection.explanation_index],
            suspected_misconception=selection.suspected_misconception,
            confidence=selection.confidence,
            corrective_guidance=context["approved_guidance"][selection.guidance_index],
        )


class TopicFeedbackProvider:
    """Structural implementation of the FeedbackProvider interface."""
    def analyze(self, context: dict) -> Analysis:
        if configuration()["mode"] == "manual":
            raise RuntimeError("Topic configured for manual feedback.")
        return analyze_answer(context)


class TopicTranslationProvider:
    """Optional Sinhala translation using this topic's provider configuration."""
    def translate(self, text: str) -> str:
        cfg = configuration()
        if cfg["mode"] == "manual":
            raise RuntimeError("Topic configured for manual translation.")
        if not cfg["model"]:
            raise RuntimeError("No model is configured for factorization translation.")

        base_url = cfg["base_url"] or DEFAULT_OLLAMA_URL
        payload = {
            "model": cfg["model"],
            "stream": False,
            "think": False,
            "options": {"temperature": 0.1, "num_predict": 200},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Translate the given text to Sinhala. "
                        "Preserve every [[MATH_n]] placeholder exactly as it is without modifying order or content."
                    ),
                },
                {"role": "user", "content": text},
            ],
        }
        with httpx.Client(timeout=_timeout(cfg), http2=False) as client:
            response = client.post(f"{base_url}/api/chat", json=payload)
            response.raise_for_status()
            return response.json()["message"]["content"].strip()
