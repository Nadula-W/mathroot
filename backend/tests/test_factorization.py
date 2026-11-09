import random
from dataclasses import replace
import pytest
from sympy import expand, simplify, sympify

from app.topics.development.factorization.generator import FactorizationTopic
from app.topics.development.factorization.manual import (
    MISCONCEPTIONS,
    generate_question,
    validate_question,
    verify_answer,
    feedback,
    teaching_recommendation,
)


def test_generated_questions_are_valid():
    """Verify at least 100 questions per difficulty level are completely valid."""
    rng = random.Random(42)
    for difficulty in ["easy", "medium", "hard"]:
        for _ in range(100):
            q = generate_question(difficulty, rng)
            validate_question(q)
            assert len(q.options) == 4
            assert len({o.id for o in q.options}) == 4
            assert len({o.text for o in q.options}) == 4
            assert q.correct_option_id in {o.id for o in q.options}
            assert next(o for o in q.options if o.id == q.correct_option_id).misconception is None
            assert simplify(sympify(q.source_expression) - sympify(q.correct_expression)) == 0
            assert len([o for o in q.options if o.misconception is None]) == 1
            assert all(o.misconception in MISCONCEPTIONS for o in q.options if o.id != q.correct_option_id)


def test_exactly_one_correct_option_without_code():
    q = generate_question("easy", random.Random(1))
    no_code = [o for o in q.options if o.misconception is None]
    assert len(no_code) == 1
    assert no_code[0].id == q.correct_option_id


def test_wrong_key_is_rejected():
    q = generate_question("easy", random.Random(2))
    wrong = next(o for o in q.options if o.id != q.correct_option_id)
    broken = replace(q, correct_option_id=wrong.id)
    with pytest.raises(ValueError):
        validate_question(broken)


def test_duplicate_option_values_rejected():
    q = generate_question("easy", random.Random(3))
    options = list(q.options)
    wrong = [o for o in options if o.id != q.correct_option_id]
    options[options.index(wrong[0])] = replace(wrong[0], text=wrong[1].text)
    with pytest.raises(ValueError):
        validate_question(replace(q, options=options))


def test_wrong_option_without_code_rejected():
    q = generate_question("easy", random.Random(4))
    options = [
        replace(o, misconception=None) if o.id != q.correct_option_id else o
        for o in q.options
    ]
    with pytest.raises(ValueError):
        validate_question(replace(q, options=options))


def test_invalid_option_format_rejected():
    q = generate_question("easy", random.Random(5))
    options = list(q.options)
    options[0] = replace(options[0], text="__import__('os')")
    with pytest.raises(ValueError):
        validate_question(replace(q, options=options))


def test_mismatched_expressions_rejected():
    q = generate_question("easy", random.Random(6))
    broken = replace(q, correct_expression="(1*x + 99)*(1*x + 99)")
    with pytest.raises(ValueError):
        validate_question(broken)


def test_verify_answer():
    q = generate_question("easy", random.Random(7))
    assert verify_answer(q, q.correct_option_id) is True
    wrong = next(o for o in q.options if o.id != q.correct_option_id)
    assert verify_answer(q, wrong.id) is False
    with pytest.raises(ValueError):
        verify_answer(q, "invalid-id")


def test_feedback_and_recommendations():
    q = generate_question("easy", random.Random(8))
    fb_correct = feedback(q, None)
    assert "Correct." in fb_correct
    assert q.explanation in fb_correct

    for code in MISCONCEPTIONS:
        fb = feedback(q, code)
        assert q.explanation in fb
        rec = teaching_recommendation(code)
        assert len(rec) > 10

    # Unknown code safe fallback
    assert "Review quadratic factorization" in teaching_recommendation("UNKNOWN_CODE")


def test_topic_adapter_and_bilingual_presentation():
    topic = FactorizationTopic()
    assert topic.topic_id == "factorization"
    assert topic.title == "Factors of Quadratic Expressions"

    q = topic.generate_question("easy")
    validate_question(q)

    # Sinhala presentation for recommendations
    si_rec = topic.presentation_text("teaching_recommendation", teaching_recommendation("SIGN_ERROR"))
    assert si_rec is not None
    assert "ලකුණු" in si_rec

    # Validation of translation
    assert topic.validate_translation("teaching_recommendation", teaching_recommendation("SIGN_ERROR"), si_rec) is True
    assert topic.validate_translation("teaching_recommendation", teaching_recommendation("SIGN_ERROR"), "Wrong text") is False


def test_sinhala_explanations_and_feedback_all_levels():
    """Verify that all difficulty levels provide complete Sinhala explanations and feedback."""
    import re
    from app.presentation import feedback_translation

    topic = FactorizationTopic()
    sinhala_pattern = re.compile(r"[\u0D80-\u0DFF]")

    for difficulty in ["easy", "medium", "hard"]:
        for seed in range(10):
            q = generate_question(difficulty, random.Random(seed))
            validate_question(q)

            # 1. Explanation translation in Sinhala
            si_expl = topic.presentation_text("explanation", q.explanation, question=q)
            assert si_expl is not None, f"Explanation translation missing for: {q.explanation}"
            assert sinhala_pattern.search(si_expl), f"Explanation has no Sinhala characters: {si_expl}"
            assert topic.validate_translation("explanation", q.explanation, si_expl, question=q) is True

            # 2. Feedback translation in Sinhala
            for code in list(MISCONCEPTIONS.keys()) + [None]:
                fb = feedback(q, code)
                si_fb = topic.presentation_text("feedback", fb, question=q)
                assert si_fb is not None, f"Feedback translation missing for code {code}"
                assert sinhala_pattern.search(si_fb), f"Feedback has no Sinhala: {si_fb}"
                assert topic.validate_translation("feedback", fb, si_fb, question=q) is True

            # 3. Full feedback_translation pipeline has zero missing field warnings
            detail = {
                "statement": q.statement,
                "explanation": q.explanation,
                "feedback": feedback(q, "SIGN_ERROR"),
                "corrective_guidance": "Check that the product of the constants equals the last term and their sum gives the middle coefficient upon expansion.",
                "teaching_recommendation": teaching_recommendation("SIGN_ERROR"),
                "suspected_misconception": "SIGN_ERROR",
            }
            res = feedback_translation(q, detail, topic)
            assert res["translation_warnings"] == [], f"Unexpected warnings: {res['translation_warnings']}"
            si_res = res["translations"]["si"]
            assert sinhala_pattern.search(si_res["explanation"])
            assert sinhala_pattern.search(si_res["feedback"])
            assert sinhala_pattern.search(si_res["statement"])

