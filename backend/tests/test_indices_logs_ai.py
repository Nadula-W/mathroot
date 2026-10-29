import json

import httpx
import pytest

from app.topics.development.indices_logs import ai, generator, manual

GOOD_PRODUCT = {
    "options": [
        {"text": "3^6", "misconception": None},
        {"text": "3^8", "misconception": "MULTIPLIED_EXPONENTS"},
        {"text": "9^6", "misconception": "MULTIPLIED_BASES"},
        {"text": "3^2", "misconception": "SUBTRACTED_EXPONENTS"},
    ],
}

GOOD_QUOTIENT = {
    "options": [
        {"text": "6^3", "misconception": None},
        {"text": "6^7", "misconception": "ADDED_EXPONENTS"},
        {"text": "6^(5/2)", "misconception": "DIVIDED_EXPONENTS"},
        {"text": "1^3", "misconception": "DIVIDED_BASES"},
    ],
}


def _copy(payload):
    return json.loads(json.dumps(payload))


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setenv("MATHROOT_INDICES_LOGS_MODE", "auto")
    monkeypatch.setenv("MATHROOT_INDICES_LOGS_MODEL", "fake-model")


SPECS = {"product": ("product", 3, 4, 2), "quotient": ("quotient", 6, 5, 2)}


def _fake_model(monkeypatch, payload, law):
    """Pretend the model replied with `payload`, and our code picked this law."""
    text = payload if isinstance(payload, str) else json.dumps(payload)
    monkeypatch.setattr(ai, "_call_ollama", lambda prompt, cfg: text)
    monkeypatch.setattr(ai, "_pick_spec", lambda: SPECS[law])


def test_good_product_question_is_accepted(configured, monkeypatch):
    _fake_model(monkeypatch, GOOD_PRODUCT, "product")
    question = ai.generate_question("easy")
    manual.validate_question(question)
    assert question.source_expression == "3^4*3^2"


def test_good_quotient_question_is_accepted(configured, monkeypatch):
    _fake_model(monkeypatch, GOOD_QUOTIENT, "quotient")
    manual.validate_question(ai.generate_question("easy"))


def test_wrong_answer_key_is_rejected(configured, monkeypatch):
    bad = _copy(GOOD_PRODUCT)
    bad["options"][0]["text"] = "3^7"  # the model "calculated" wrongly
    _fake_model(monkeypatch, bad, "product")
    with pytest.raises(ValueError):
        manual.validate_question(ai.generate_question("easy"))


def test_false_diagnosis_is_rejected(configured, monkeypatch):
    bad = _copy(GOOD_PRODUCT)
    bad["options"][1]["misconception"] = "SUBTRACTED_EXPONENTS"  # wrong label
    bad["options"][3]["misconception"] = "MULTIPLIED_EXPONENTS"  # wrong label
    _fake_model(monkeypatch, bad, "product")
    with pytest.raises(ValueError):
        manual.validate_question(ai.generate_question("easy"))


def test_code_from_the_wrong_law_is_rejected(configured, monkeypatch):
    bad = _copy(GOOD_PRODUCT)
    bad["options"][1]["misconception"] = "ADDED_EXPONENTS"
    _fake_model(monkeypatch, bad, "product")
    with pytest.raises(ValueError):
        manual.validate_question(ai.generate_question("easy"))


def test_two_correct_options_are_rejected(configured, monkeypatch):
    bad = _copy(GOOD_PRODUCT)
    bad["options"][1]["misconception"] = None
    _fake_model(monkeypatch, bad, "product")
    with pytest.raises(ValueError):
        ai.generate_question("easy")


@pytest.mark.parametrize("payload", [
    "this is not json",
    {"statement": "Simplify: 3^4 × 3^2"},
    {"options": GOOD_PRODUCT["options"][:3]},
])
def test_bad_model_output_raises(configured, monkeypatch, payload):
    _fake_model(monkeypatch, payload, "product")
    with pytest.raises(ValueError):
        ai.generate_question("easy")


def test_option_with_extra_words_is_rejected(configured, monkeypatch):
    bad = _copy(GOOD_PRODUCT)
    bad["options"][0]["text"] = "3^4 × 3^2 = 3^6"   # what the model did in v1
    _fake_model(monkeypatch, bad, "product")
    with pytest.raises(ValueError):
        manual.validate_question(ai.generate_question("easy"))


def test_statement_comes_from_our_code(configured, monkeypatch):
    _fake_model(monkeypatch, GOOD_PRODUCT, "product")
    assert ai.generate_question("easy").statement == "Simplify: 3^4 × 3^2"


def test_prompt_contains_the_numbers():
    prompt = ai._build_prompt("quotient", 6, 5, 2, "easy")
    assert "Simplify: 6^5 ÷ 6^2" in prompt
    assert "DIVIDED_BASES" in prompt


def test_missing_model_raises(monkeypatch):
    monkeypatch.delenv("MATHROOT_INDICES_LOGS_MODEL", raising=False)
    with pytest.raises(RuntimeError):
        ai.generate_question("easy")


def test_generator_falls_back_when_ai_is_down(configured, monkeypatch):
    def broken(prompt, cfg):
        raise httpx.ConnectError("Ollama is not running")
    monkeypatch.setattr(ai, "_call_ollama", broken)
    manual.validate_question(generator.generate_question("easy"))


def test_generator_falls_back_when_ai_lies(configured, monkeypatch):
    bad = _copy(GOOD_PRODUCT)
    bad["options"][0]["text"] = "3^7"
    _fake_model(monkeypatch, bad, "product")
    question = generator.generate_question("easy")
    manual.validate_question(question)
    assert question.explanation  # a valid question came back anyway