import json
import httpx
import pytest

from app.topics.development.factorization import ai, generator, manual

GOOD_AI_RESPONSE = {
    "options": [
        {"text": "(x - 4)(x + 4)", "misconception": None},
        {"text": "(x - 4)(x - 4)", "misconception": "SIGN_ERROR"},
        {"text": "(x - 16)(x + 16)", "misconception": "SQUARES_SQUARE_ROOT_ERROR"},
        {"text": "(x + 4)(x + 4)", "misconception": "SUM_PRODUCT_CONFUSION"},
    ]
}


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setenv("MATHROOT_FACTORIZATION_MODE", "auto")
    monkeypatch.setenv("MATHROOT_FACTORIZATION_MODEL", "test-model")


def _fake_model(monkeypatch, payload):
    text = payload if isinstance(payload, str) else json.dumps(payload)
    monkeypatch.setattr(ai, "_call_ollama", lambda prompt, cfg: text)
    monkeypatch.setattr(ai, "_pick_spec", lambda diff: (1, 0, -16, "(x - 4)(x + 4)"))


def test_good_ai_question_accepted(configured, monkeypatch):
    _fake_model(monkeypatch, GOOD_AI_RESPONSE)
    q = ai.generate_question("easy")
    manual.validate_question(q)
    assert q.source_expression == "1*x**2 + (-16)"


def test_wrong_answer_key_rejected(configured, monkeypatch):
    bad = json.loads(json.dumps(GOOD_AI_RESPONSE))
    bad["options"][0]["text"] = "(x - 5)(x + 5)"
    _fake_model(monkeypatch, bad)
    with pytest.raises(ValueError):
        manual.validate_question(ai.generate_question("easy"))


def test_malformed_json_raises(configured, monkeypatch):
    _fake_model(monkeypatch, "this is not json")
    with pytest.raises(Exception):
        ai.generate_question("easy")


def test_missing_model_raises(monkeypatch):
    monkeypatch.delenv("MATHROOT_FACTORIZATION_MODEL", raising=False)
    with pytest.raises(RuntimeError):
        ai.generate_question("easy")


def test_generator_fallback_when_ai_down(configured, monkeypatch):
    def broken(prompt, cfg):
        raise httpx.ConnectError("Ollama offline")

    monkeypatch.setattr(ai, "_call_ollama", broken)
    for difficulty in ["easy", "medium", "hard"]:
        q = generator.generate_question(difficulty)
        manual.validate_question(q)
        assert q.difficulty == difficulty
        assert q.explanation


def test_generator_fallback_when_ai_hallucinates(configured, monkeypatch):
    bad = json.loads(json.dumps(GOOD_AI_RESPONSE))
    bad["options"][0]["text"] = "(x - 99)(x + 99)"
    _fake_model(monkeypatch, bad)
    for difficulty in ["easy", "medium", "hard"]:
        q = generator.generate_question(difficulty)
        manual.validate_question(q)
        assert q.difficulty == difficulty
        assert q.explanation


def test_hard_ai_spec_diversity():
    """Verify hard AI question generation produces diverse questions without duplicates."""
    from sympy import Symbol, expand, simplify
    x = Symbol("x")

    specs = set()
    for _ in range(60):
        a, b, c, factors = ai._pick_spec("hard")
        specs.add((a, b, c, factors))
        poly = manual._parse_option_expr(factors)
        expected = expand(a * x**2 + b * x + c)
        assert simplify(poly - expected) == 0

    # Ensure a rich variety of different quadratic questions are generated
    assert len(specs) >= 10, f"Expected at least 10 distinct specs, got {len(specs)}"


def test_manual_mode_generation_all_levels(monkeypatch):
    monkeypatch.setenv("MATHROOT_FACTORIZATION_MODE", "manual")
    for difficulty in ["easy", "medium", "hard"]:
        for _ in range(5):
            q = generator.generate_question(difficulty)
            manual.validate_question(q)
            assert q.difficulty == difficulty
            assert q.explanation

