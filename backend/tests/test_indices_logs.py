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


ALL_LAWS = ["product", "quotient", "power", "tolog", "toindex",
            "logvalue", "logsum", "logdiff", "logpower"]


@pytest.mark.parametrize("law", ALL_LAWS)
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


def test_conversion_laws_have_expected_codes():
    tolog = generate_question("easy", random.Random(31), law="tolog")
    assert {o.misconception for o in tolog.options} == {
        None, "LOG_BASE_AND_NUMBER_SWAPPED", "LOG_BASE_AND_RESULT_SWAPPED",
        "LOG_NUMBER_AND_RESULT_SWAPPED",
    }
    toindex = generate_question("easy", random.Random(32), law="toindex")
    assert {o.misconception for o in toindex.options} == {
        None, "INDEX_BASE_AND_EXPONENT_SWAPPED", "INDEX_BASE_AND_VALUE_SWAPPED",
        "INDEX_EXPONENT_AND_VALUE_SWAPPED",
    }


def test_trap_spec_is_never_used():
    from app.topics.development.indices_logs.manual import conversion_specs
    # 2^4 = 16 and 4^2 = 16: the "swapped" statement would ALSO be true
    assert (2, 4) not in conversion_specs("tolog")
    assert (2, 4) not in conversion_specs("toindex")


def _hand_built_tolog(base, e, texts):
    """Make a tolog question from our generator, then overwrite it with chosen options."""
    question = generate_question("easy", random.Random(33), law="tolog")
    options = [replace(o, text=t, misconception=c) for o, (t, c) in zip(question.options, texts)]
    value = base ** e
    return replace(
        question,
        source_expression=f"{base}^{e}={value}",
        correct_expression=texts[0][0],
        options=options,
        correct_option_id=options[0].id,
    )


def test_hand_built_conversion_question_passes():
    question = _hand_built_tolog(2, 3, [
        ("log_2 8 = 3", None),
        ("log_8 2 = 3", "LOG_BASE_AND_NUMBER_SWAPPED"),
        ("log_3 8 = 2", "LOG_BASE_AND_RESULT_SWAPPED"),
        ("log_2 3 = 8", "LOG_NUMBER_AND_RESULT_SWAPPED"),
    ])
    validate_question(question)


def test_true_wrong_statement_is_rejected():
    # 4^2 = 16 is also true, so "log_4 16 = 2" is a second correct answer
    question = _hand_built_tolog(2, 4, [
        ("log_2 16 = 4", None),
        ("log_16 2 = 4", "LOG_BASE_AND_NUMBER_SWAPPED"),
        ("log_4 16 = 2", "LOG_BASE_AND_RESULT_SWAPPED"),
        ("log_2 4 = 16", "LOG_NUMBER_AND_RESULT_SWAPPED"),
    ])
    with pytest.raises(ValueError):
        validate_question(question)


def test_false_question_statement_is_rejected():
    question = generate_question("easy", random.Random(34), law="tolog")
    with pytest.raises(ValueError):
        validate_question(replace(question, source_expression="2^5=33"))


def test_unreadable_statement_is_rejected():
    question = generate_question("easy", random.Random(35), law="toindex")
    options = list(question.options)
    options[0] = replace(options[0], text="__import__('os') = 1")
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))


def test_huge_conversion_numbers_do_not_hang():
    question = generate_question("easy", random.Random(36), law="toindex")
    options = list(question.options)
    options[0] = replace(options[0], text="2^999999 = 4")
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))


def test_log_laws_have_expected_codes():
    expected = {
        "logvalue": {"DIVIDED_VALUE_BY_BASE", "SUBTRACTED_BASE_FROM_VALUE",
                     "COUNTED_MULTIPLICATION_SIGNS"},
        "logsum": {"LOG_OF_SUM", "MULTIPLIED_LOG_VALUES", "LOGS_IGNORED_NUMBERS_ADDED"},
        "logdiff": {"LOG_OF_DIFFERENCE", "DIVIDED_LOG_VALUES", "LOGS_IGNORED_NUMBERS_DIVIDED"},
        "logpower": {"LOG_RAISED_TO_POWER", "POWER_ADDED_TO_LOG", "POWER_IGNORED"},
    }
    for law, codes in expected.items():
        question = generate_question("easy", random.Random(40), law=law)
        assert {o.misconception for o in question.options} == codes | {None}


def test_every_log_spec_has_four_different_values():
    from app.topics.development.indices_logs.manual import log_specs
    for law in ["logvalue", "logsum", "logdiff", "logpower"]:
        assert len(log_specs(law)) >= 5


def test_log_option_that_equals_the_answer_is_rejected():
    # "log_2 8" is just another way to write 3, so it must not be a wrong option
    question = generate_question("easy", random.Random(41), law="logsum")
    wrong = next(o for o in question.options if o.misconception == "LOG_OF_SUM")
    options = [replace(o, text="log_2 8") if o.id == wrong.id else o for o in question.options]
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))


def test_logs_that_are_not_whole_powers_are_rejected_in_the_question():
    question = generate_question("easy", random.Random(42), law="logvalue")
    with pytest.raises(ValueError):
        validate_question(replace(question, source_expression="log_2 12"))


def test_decimal_and_log_text_are_read_safely():
    question = generate_question("easy", random.Random(43), law="logdiff")
    options = list(question.options)
    options[0] = replace(options[0], text="2.5.5")
    with pytest.raises(ValueError):
        validate_question(replace(question, options=options))


def test_log_codes_must_match_their_values():
    question = generate_question("easy", random.Random(44), law="logpower")
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
