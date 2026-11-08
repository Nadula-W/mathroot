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


GOOD_POWER = {
    "options": [
        {"text": "2^6", "misconception": None},
        {"text": "2^5", "misconception": "ADDED_EXPONENTS_POWER"},
        {"text": "2 × 2^3", "misconception": "EXPONENT_AS_MULTIPLIER"},
        {"text": "2^9", "misconception": "POWER_ONLY_ON_EXPONENT"},
    ],
}


GOOD_TOLOG = {
    "options": [
        {"text": "log_2 32 = 5", "misconception": None},
        {"text": "log_32 2 = 5", "misconception": "LOG_BASE_AND_NUMBER_SWAPPED"},
        {"text": "log_5 32 = 2", "misconception": "LOG_BASE_AND_RESULT_SWAPPED"},
        {"text": "log_2 5 = 32", "misconception": "LOG_NUMBER_AND_RESULT_SWAPPED"},
    ],
}

GOOD_TOINDEX = {
    "options": [
        {"text": "3^4 = 81", "misconception": None},
        {"text": "4^3 = 81", "misconception": "INDEX_BASE_AND_EXPONENT_SWAPPED"},
        {"text": "81^4 = 3", "misconception": "INDEX_BASE_AND_VALUE_SWAPPED"},
        {"text": "3^81 = 4", "misconception": "INDEX_EXPONENT_AND_VALUE_SWAPPED"},
    ],
}


GOOD_LOGS = {
    "logvalue": {"options": [
        {"text": "5", "misconception": None},
        {"text": "16", "misconception": "DIVIDED_VALUE_BY_BASE"},
        {"text": "30", "misconception": "SUBTRACTED_BASE_FROM_VALUE"},
        {"text": "4", "misconception": "COUNTED_MULTIPLICATION_SIGNS"},
    ]},
    "logsum": {"options": [
        {"text": "5", "misconception": None},
        {"text": "log_2 12", "misconception": "LOG_OF_SUM"},
        {"text": "6", "misconception": "MULTIPLIED_LOG_VALUES"},
        {"text": "12", "misconception": "LOGS_IGNORED_NUMBERS_ADDED"},
    ]},
    "logdiff": {"options": [
        {"text": "3", "misconception": None},
        {"text": "log_2 28", "misconception": "LOG_OF_DIFFERENCE"},
        {"text": "2.5", "misconception": "DIVIDED_LOG_VALUES"},
        {"text": "8", "misconception": "LOGS_IGNORED_NUMBERS_DIVIDED"},
    ]},
    "logpower": {"options": [
        {"text": "6", "misconception": None},
        {"text": "8", "misconception": "LOG_RAISED_TO_POWER"},
        {"text": "5", "misconception": "POWER_ADDED_TO_LOG"},
        {"text": "2", "misconception": "POWER_IGNORED"},
    ]},
}


def _copy(payload):
    return json.loads(json.dumps(payload))


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setenv("MATHROOT_INDICES_LOGS_MODE", "auto")
    monkeypatch.setenv("MATHROOT_INDICES_LOGS_MODEL", "fake-model")


SPECS = {
    "product": ("product", 3, 4, 2),
    "quotient": ("quotient", 6, 5, 2),
    "power": ("power", 2, 3, 2),
    "tolog": ("tolog", 2, 5, 32),       # 2^5 = 32
    "toindex": ("toindex", 3, 4, 81),   # log_3 81 = 4
    "logvalue": ("logvalue", 2, 5, 32),  # log_2 32
    "logsum": ("logsum", 2, 2, 3),       # log_2 4 + log_2 8
    "logdiff": ("logdiff", 2, 5, 2),     # log_2 32 - log_2 4
    "logpower": ("logpower", 2, 2, 3),   # log_2 (4^3)
}


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


def test_good_power_question_is_accepted(configured, monkeypatch):
    _fake_model(monkeypatch, GOOD_POWER, "power")
    question = ai.generate_question("easy")
    manual.validate_question(question)
    assert question.statement == "Simplify: (2^3)^2"


def test_power_question_with_swapped_codes_is_rejected(configured, monkeypatch):
    bad = _copy(GOOD_POWER)
    bad["options"][1]["misconception"] = "POWER_ONLY_ON_EXPONENT"
    bad["options"][3]["misconception"] = "ADDED_EXPONENTS_POWER"
    _fake_model(monkeypatch, bad, "power")
    with pytest.raises(ValueError):
        manual.validate_question(ai.generate_question("easy"))


def test_good_conversion_questions_are_accepted(configured, monkeypatch):
    _fake_model(monkeypatch, GOOD_TOLOG, "tolog")
    question = ai.generate_question("easy")
    manual.validate_question(question)
    assert question.statement == "Write 2^5 = 32 in logarithmic form."
    _fake_model(monkeypatch, GOOD_TOINDEX, "toindex")
    question = ai.generate_question("easy")
    manual.validate_question(question)
    assert question.statement == "Write log_3 81 = 4 in index form."


def test_model_cannot_slip_in_a_second_true_statement(configured, monkeypatch):
    # 2^4 = 16 and 4^2 = 16, so "log_4 16 = 2" is ALSO true: not allowed as a wrong option
    bad = {"options": [
        {"text": "log_2 16 = 4", "misconception": None},
        {"text": "log_16 2 = 4", "misconception": "LOG_BASE_AND_NUMBER_SWAPPED"},
        {"text": "log_4 16 = 2", "misconception": "LOG_BASE_AND_RESULT_SWAPPED"},
        {"text": "log_2 4 = 16", "misconception": "LOG_NUMBER_AND_RESULT_SWAPPED"},
    ]}
    monkeypatch.setattr(ai, "_call_ollama", lambda prompt, cfg: json.dumps(bad))
    monkeypatch.setattr(ai, "_pick_spec", lambda: ("tolog", 2, 4, 16))
    with pytest.raises(ValueError):
        manual.validate_question(ai.generate_question("easy"))


def test_conversion_with_swapped_codes_is_rejected(configured, monkeypatch):
    bad = _copy(GOOD_TOINDEX)
    bad["options"][1]["misconception"] = "INDEX_BASE_AND_VALUE_SWAPPED"
    bad["options"][2]["misconception"] = "INDEX_BASE_AND_EXPONENT_SWAPPED"
    _fake_model(monkeypatch, bad, "toindex")
    with pytest.raises(ValueError):
        manual.validate_question(ai.generate_question("easy"))


@pytest.mark.parametrize("law", ["logvalue", "logsum", "logdiff", "logpower"])
def test_good_log_questions_are_accepted(configured, monkeypatch, law):
    _fake_model(monkeypatch, GOOD_LOGS[law], law)
    manual.validate_question(ai.generate_question("easy"))


def test_statements_of_log_questions_come_from_our_code(configured, monkeypatch):
    expected = {
        "logvalue": "Find the value of log_2 32.",
        "logsum": "Find the value of log_2 4 + log_2 8.",
        "logdiff": "Find the value of log_2 32 - log_2 4.",
        "logpower": "Find the value of log_2 (4^3).",
    }
    for law, statement in expected.items():
        _fake_model(monkeypatch, GOOD_LOGS[law], law)
        assert ai.generate_question("easy").statement == statement


def test_log_question_with_false_diagnosis_is_rejected(configured, monkeypatch):
    bad = _copy(GOOD_LOGS["logsum"])
    bad["options"][2]["misconception"] = "LOGS_IGNORED_NUMBERS_ADDED"   # 6 is not 4 + 8
    bad["options"][3]["misconception"] = "MULTIPLIED_LOG_VALUES"        # 12 is not 2 x 3
    _fake_model(monkeypatch, bad, "logsum")
    with pytest.raises(ValueError):
        manual.validate_question(ai.generate_question("easy"))


def test_every_prompt_example_is_a_valid_question():
    """The example inside each prompt must itself pass our validator."""
    example_specs = {
        "product": ("product", 7, 5, 3),
        "quotient": ("quotient", 7, 7, 3),
        "power": ("power", 7, 2, 3),
        "tolog": ("tolog", 7, 2, 49),
        "toindex": ("toindex", 7, 2, 49),
        "logvalue": ("logvalue", 7, 3, 343),
        "logsum": ("logsum", 7, 2, 3),
        "logdiff": ("logdiff", 7, 5, 2),
        "logpower": ("logpower", 7, 2, 3),
    }
    for law, spec in example_specs.items():
        statement, example_json = ai._EXAMPLES[law]
        question = ai._to_question(example_json, spec, "easy")
        assert question.statement == statement
        manual.validate_question(question)


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

# ---------- AI timeout: validated and limited ----------

TIMEOUT_NAME = "MATHROOT_INDICES_LOGS_TIMEOUT_SECONDS"


def test_timeout_defaults_to_four_seconds(monkeypatch):
    monkeypatch.delenv(TIMEOUT_NAME, raising=False)
    assert ai.configuration()["timeout_seconds"] == 4.0


@pytest.mark.parametrize("value, expected", [
    ("7.5", 7.5),
    ("0.1", 0.1),     # lowest allowed
    ("15", 15.0),     # highest allowed
    ("1", 1.0),
])
def test_timeout_inside_the_limits_is_used(monkeypatch, value, expected):
    monkeypatch.setenv(TIMEOUT_NAME, value)
    assert ai.configuration()["timeout_seconds"] == expected


@pytest.mark.parametrize("value", [
    "abc", "", "  ", "0", "-3", "0.05", "15.01", "60", "999999", "nan", "inf", "-inf", "4;5",
])
def test_bad_timeout_values_use_the_default(monkeypatch, value):
    monkeypatch.setenv(TIMEOUT_NAME, value)
    assert ai.configuration()["timeout_seconds"] == 4.0


class _FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"message": {"content": json.dumps(GOOD_PRODUCT)}}


def _capture_http_timeout(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["timeout"] = timeout
        return _FakeResponse()

    monkeypatch.setattr(ai.httpx, "post", fake_post)
    monkeypatch.setattr(ai, "_pick_spec", lambda: SPECS["product"])
    return captured


def test_the_checked_timeout_reaches_the_http_call(configured, monkeypatch):
    captured = _capture_http_timeout(monkeypatch)
    monkeypatch.setenv(TIMEOUT_NAME, "7.5")
    manual.validate_question(ai.generate_question("easy"))
    assert captured["timeout"] == 7.5


def test_a_huge_timeout_setting_cannot_reach_the_http_call(configured, monkeypatch):
    captured = _capture_http_timeout(monkeypatch)
    monkeypatch.setenv(TIMEOUT_NAME, "999")
    ai.generate_question("easy")
    assert captured["timeout"] == 4.0


@pytest.mark.parametrize("error", [
    httpx.ReadTimeout("model too slow"),
    httpx.ConnectTimeout("cannot connect in time"),
])
def test_generator_falls_back_when_the_model_times_out(configured, monkeypatch, error):
    def too_slow(prompt, cfg):
        raise error
    monkeypatch.setattr(ai, "_call_ollama", too_slow)
    manual.validate_question(generator.generate_question("easy"))