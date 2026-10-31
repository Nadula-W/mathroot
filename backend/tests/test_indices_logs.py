import random
from dataclasses import replace
import pytest

from app.topics.development.indices_logs.manual import (
    generate_question,
    validate_question,
    verify_answer,
)


def test_generated_questions_are_valid():
    rng = random.Random(7)
    for difficulty in ["easy", "medium", "hard"]:
        for _ in range(100):
            question = generate_question(difficulty, rng)
            validate_question(question)  # must not raise


def test_exactly_one_correct_option_without_code():
    question = generate_question("easy", random.Random(1))
    no_code = [o for o in question.options if o.misconception is None]
    assert len(no_code) == 1
    assert no_code[0].id == question.correct_option_id


def test_wrong_key_is_rejected():
    question = generate_question("easy", random.Random(2))
    wrong = next(o for o in question.options if o.id != question.correct_option_id)
    broken = replace(question, correct_option_id=wrong.id)
    with pytest.raises(ValueError):
        validate_question(broken)


def test_duplicate_values_are_rejected():
    question = generate_question("easy", random.Random(3))
    options = list(question.options)
    wrong = [o for o in options if o.id != question.correct_option_id]
    options[options.index(wrong[0])] = replace(wrong[0], text=wrong[1].text)
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))


def test_wrong_option_without_code_is_rejected():
    question = generate_question("easy", random.Random(4))
    options = [
        replace(o, misconception=None) if o.id != question.correct_option_id else o
        for o in question.options
    ]
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))


def test_unreadable_option_text_is_rejected():
    question = generate_question("easy", random.Random(5))
    options = list(question.options)
    options[0] = replace(options[0], text="__import__('os')")
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))


def test_huge_exponent_is_rejected_quickly():
    question = generate_question("easy", random.Random(6))
    bad = replace(question, source_expression="2^99999999*2^3")
    with pytest.raises(ValueError):
        validate_question(bad)


def test_verify_answer():
    question = generate_question("easy", random.Random(8))
    assert verify_answer(question, question.correct_option_id) is True
    wrong = next(o for o in question.options if o.id != question.correct_option_id)
    assert verify_answer(question, wrong.id) is False
    with pytest.raises(ValueError):
        verify_answer(question, "not-an-id")

@pytest.mark.parametrize("law", ["product", "quotient", "power"])
def test_each_law_generates_valid_questions(law):
    rng = random.Random(11)
    for _ in range(200):
        validate_question(generate_question("easy", rng, law=law))


def test_quotient_has_expected_codes():
    question = generate_question("easy", random.Random(12), law="quotient")
    codes = {o.misconception for o in question.options}
    assert codes == {None, "ADDED_EXPONENTS", "DIVIDED_EXPONENTS", "DIVIDED_BASES"}


def test_zero_denominator_is_rejected():
    question = generate_question("easy", random.Random(13), law="quotient")
    options = list(question.options)
    options[0] = replace(options[0], text="6^(5/0)")
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))


def test_unknown_law_is_rejected():
    with pytest.raises(ValueError):
        generate_question("easy", random.Random(14), law="cubic")
        
def test_swapped_codes_are_rejected():
    question = generate_question("easy", random.Random(21), law="product")
    wrong = [o for o in question.options if o.id != question.correct_option_id]
    a, b = wrong[0], wrong[1]
    options = [
        replace(o, misconception=b.misconception) if o.id == a.id
        else replace(o, misconception=a.misconception) if o.id == b.id
        else o
        for o in question.options
    ]
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))

def test_power_has_expected_codes():
    question = generate_question("easy", random.Random(15), law="power")
    codes = {o.misconception for o in question.options}
    assert codes == {
        None, "ADDED_EXPONENTS_POWER", "EXPONENT_AS_MULTIPLIER", "POWER_ONLY_ON_EXPONENT",
    }


def test_power_options_are_all_different_for_every_spec():
    from app.topics.development.indices_logs.manual import power_specs
    assert len(power_specs()) > 5
    for base, m, n in power_specs():
        values = {base ** (m * n), base ** (m + n), n * base ** m, base ** (m ** n)}
        assert len(values) == 4


def test_power_codes_must_match_their_values():
    question = generate_question("easy", random.Random(16), law="power")
    wrong = [o for o in question.options if o.id != question.correct_option_id]
    a, b = wrong[0], wrong[1]
    options = [
        replace(o, misconception=b.misconception) if o.id == a.id
        else replace(o, misconception=a.misconception) if o.id == b.id
        else o
        for o in question.options
    ]
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))


def test_code_from_another_law_is_rejected_for_power():
    question = generate_question("easy", random.Random(17), law="power")
    wrong = next(o for o in question.options if o.id != question.correct_option_id)
    options = [
        replace(o, misconception="MULTIPLIED_EXPONENTS") if o.id == wrong.id else o
        for o in question.options
    ]
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))


def test_unreadable_multiple_is_rejected():
    question = generate_question("easy", random.Random(18), law="power")
    options = list(question.options)
    options[0] = replace(options[0], text="2 x x 2^3")
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))