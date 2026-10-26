"""Tests for Algebraic Fractions remediation workflow, parameter exclusion, persistence, and scoring integrity."""
from dataclasses import asdict
from unittest.mock import patch

import pytest

from app.contracts import InternalOption, InternalQuestion
from app.topics.development.algebraic_fractions import ai, generator, manual
from app.topics.development.algebraic_fractions.generator import AlgebraicFractionsTopic
from app.topics.development.binomial.manual import BinomialTopic


def enroll(client, class_id="demo3", join_code="secret-code"):
    return client.post("/api/classes/join", json={"class_id": class_id, "join_code": join_code})


def seed_af_test(client, difficulties=("easy",), test_id="af-test"):
    topic = AlgebraicFractionsTopic()
    questions = [asdict(topic.generate_question(d)) for d in difficulties]
    client.db.setdefault("mathroot_tests", []).append({
        "id": test_id,
        "title": "Algebraic Fractions Test",
        "class_id": "demo3",
        "teacher_id": "teacher",
        "questions": questions,
    })
    return questions


def seed_binomial_test(client, test_id="bin-test"):
    topic = BinomialTopic()
    questions = [asdict(topic.generate_question("easy"))]
    client.db.setdefault("mathroot_tests", []).append({
        "id": test_id,
        "title": "Binomial Test",
        "class_id": "demo3",
        "teacher_id": "teacher",
        "questions": questions,
    })
    return questions


def test_remediation_triggered_on_wrong_algebraic_fractions_answer(client):
    questions = seed_af_test(client, ("easy",))
    enroll(client)
    q0 = questions[0]

    # Select an incorrect option
    wrong_opt = next(o["id"] for o in q0["options"] if o["id"] != q0["correct_option_id"])
    res = client.post("/api/tests/af-test/answers/submit", json={
        "question_id": q0["id"],
        "option_id": wrong_opt,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["correct"] is False
    assert "remediation" in data
    rem = data["remediation"]
    assert rem["status"] == "active"
    assert rem["attempt_number"] == 1

    rem_q = rem["question"]
    assert rem_q is not None
    assert rem_q["topic_id"] == "algebraic_fractions"
    assert rem_q["difficulty"] == "easy"
    assert "statement" in rem_q
    assert len(rem_q["options"]) == 4

    # Security: No correct answer keys or misconceptions leaked in public question
    assert "correct_option_id" not in rem_q
    assert "misconception" not in str(rem_q["options"])

    # Reviewed Sinhala presentation included
    assert "statement" in rem_q.get("translations", {}).get("si", {})

    # Parameter distinctness: must not repeat original parameters
    q0_obj = InternalQuestion(**{**q0, "options": [InternalOption(**o) for o in q0["options"]]})
    _, p0 = manual.extract_question_parameters(q0_obj)

    db_row = client.db["mathroot_answers"][0]
    rem_stored = db_row["verification"]["remediation"]["current_question"]
    rem_q_obj = InternalQuestion(**{**rem_stored, "options": [InternalOption(**o) for o in rem_stored["options"]]})
    _, p_rem = manual.extract_question_parameters(rem_q_obj)
    assert p_rem != p0

    # Official scoring: exactly 1 answer row, 0 correct, not completed because remediation active
    prog = client.get("/api/tests/af-test/progress").json()
    assert prog["answered"] == 1
    assert prog["correct"] == 0
    assert prog["incorrect"] == 1
    assert prog["percentage"] == 0.0
    assert prog["status"] == "In Progress"
    assert len(client.db["mathroot_answers"]) == 1


def test_repeated_wrong_remediation_answers_produce_unseen_variations(client):
    questions = seed_af_test(client, ("easy",))
    enroll(client)
    q0 = questions[0]

    # Initial wrong answer
    wrong_opt = next(o["id"] for o in q0["options"] if o["id"] != q0["correct_option_id"])
    res1 = client.post("/api/tests/af-test/answers/submit", json={
        "question_id": q0["id"],
        "option_id": wrong_opt,
    })
    rem1 = res1.json()["remediation"]
    assert rem1["status"] == "active"
    assert rem1["attempt_number"] == 1

    # Inspect server-side stored remediation question to find a distractor
    db_row = client.db["mathroot_answers"][0]
    rem_stored_1 = db_row["verification"]["remediation"]["current_question"]
    rem1_correct_id = rem_stored_1["correct_option_id"]
    rem1_wrong_opt = next(o["id"] for o in rem_stored_1["options"] if o["id"] != rem1_correct_id)

    # Submit wrong answer to remediation variation 1
    res2 = client.post("/api/tests/af-test/answers/submit", json={
        "question_id": rem_stored_1["id"],
        "option_id": rem1_wrong_opt,
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["correct"] is False
    assert "feedback" in data2
    assert "remediation" in data2

    rem2 = data2["remediation"]
    assert rem2["status"] == "active"
    assert rem2["attempt_number"] == 2

    # Check variation 2 has distinct parameters from both q0 and variation 1
    q0_obj = InternalQuestion(**{**q0, "options": [InternalOption(**o) for o in q0["options"]]})
    _, p0 = manual.extract_question_parameters(q0_obj)

    q1_obj = InternalQuestion(**{**rem_stored_1, "options": [InternalOption(**o) for o in rem_stored_1["options"]]})
    _, p1 = manual.extract_question_parameters(q1_obj)

    rem_stored_2 = db_row["verification"]["remediation"]["current_question"]
    q2_obj = InternalQuestion(**{**rem_stored_2, "options": [InternalOption(**o) for o in rem_stored_2["options"]]})
    _, p2 = manual.extract_question_parameters(q2_obj)

    assert p0 != p1
    assert p2 != p0
    assert p2 != p1

    seen = [tuple(p) for p in db_row["verification"]["remediation"]["seen_params"]]
    assert seen == [p0, p1, p2]

    # Official scoring and answer rows unchanged
    assert len(client.db["mathroot_answers"]) == 1
    prog = client.get("/api/tests/af-test/progress").json()
    assert prog["answered"] == 1
    assert prog["correct"] == 0
    assert prog["incorrect"] == 1


def test_correct_remediation_answer_terminates_remediation_and_preserves_score(client):
    questions = seed_af_test(client, ("easy",))
    enroll(client)
    q0 = questions[0]

    # Initial wrong answer
    wrong_opt = next(o["id"] for o in q0["options"] if o["id"] != q0["correct_option_id"])
    client.post("/api/tests/af-test/answers/submit", json={
        "question_id": q0["id"],
        "option_id": wrong_opt,
    })

    # Find the correct answer for the remediation question
    db_row = client.db["mathroot_answers"][0]
    rem_stored = db_row["verification"]["remediation"]["current_question"]
    correct_rem_opt = rem_stored["correct_option_id"]

    # Submit correct answer to remediation
    res = client.post("/api/tests/af-test/answers/submit", json={
        "question_id": rem_stored["id"],
        "option_id": correct_rem_opt,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["correct"] is True
    assert data["remediation"]["status"] == "completed"
    assert data["remediation"]["question"] is None

    # Verify official scoring is strictly based on the first scheduled answer:
    # Student still has 0 correct for the official test, percentage 0%
    prog = client.get("/api/tests/af-test/progress").json()
    assert prog["answered"] == 1
    assert prog["correct"] == 0
    assert prog["incorrect"] == 1
    assert prog["percentage"] == 0.0
    # Because remediation is completed and all scheduled questions are answered, test is now Completed
    assert prog["status"] == "Completed"
    assert len(client.db["mathroot_answers"]) == 1


def test_correct_original_answer_does_not_start_remediation(client):
    questions = seed_af_test(client, ("easy",))
    enroll(client)
    q0 = questions[0]

    res = client.post("/api/tests/af-test/answers/submit", json={
        "question_id": q0["id"],
        "option_id": q0["correct_option_id"],
    })
    assert res.status_code == 200
    data = res.json()
    assert data["correct"] is True
    assert data.get("remediation") is None

    db_row = client.db["mathroot_answers"][0]
    assert "remediation" not in db_row["verification"]

    prog = client.get("/api/tests/af-test/progress").json()
    assert prog["answered"] == 1
    assert prog["correct"] == 1
    assert prog["percentage"] == 100.0
    assert prog["status"] == "Completed"


def test_non_algebraic_fractions_topic_does_not_start_remediation(client):
    questions = seed_binomial_test(client, "bin-test")
    enroll(client)
    q0 = questions[0]

    wrong_opt = next(o["id"] for o in q0["options"] if o["id"] != q0["correct_option_id"])
    res = client.post("/api/tests/bin-test/answers/submit", json={
        "question_id": q0["id"],
        "option_id": wrong_opt,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["correct"] is False
    assert data.get("remediation") is None

    db_row = client.db["mathroot_answers"][0]
    assert "remediation" not in db_row["verification"]


def test_page_reload_and_resume_persistence_during_remediation(client):
    questions = seed_af_test(client, ("easy", "medium"))
    enroll(client)
    q0 = questions[0]

    wrong_opt = next(o["id"] for o in q0["options"] if o["id"] != q0["correct_option_id"])
    client.post("/api/tests/af-test/answers/submit", json={
        "question_id": q0["id"],
        "option_id": wrong_opt,
    })

    # Simulate browser reload by calling progress and review endpoints
    prog = client.get("/api/tests/af-test/progress").json()
    assert prog["status"] == "In Progress"
    assert "active_remediation" in prog
    active_rem = prog["active_remediation"]
    assert active_rem["status"] == "active"
    assert active_rem["scheduled_question_id"] == q0["id"]
    assert active_rem["attempt_number"] == 1
    assert active_rem["question"]["question_id"] is not None
    assert "correct_option_id" not in active_rem["question"]

    # Student can still retrieve test questions without leaking keys
    test_pub = client.get("/api/tests/af-test").json()
    assert len(test_pub["questions"]) == 2
    assert "correct_option_id" not in str(test_pub)


def test_multi_question_test_advances_to_next_question_after_remediation(client):
    questions = seed_af_test(client, ("easy", "medium"))
    enroll(client)
    q0, q1 = questions[0], questions[1]

    # Question 0: answered incorrectly, starts remediation
    w0 = next(o["id"] for o in q0["options"] if o["id"] != q0["correct_option_id"])
    client.post("/api/tests/af-test/answers/submit", json={"question_id": q0["id"], "option_id": w0})

    # Complete remediation for Q0
    db_row0 = client.db["mathroot_answers"][0]
    rem_stored = db_row0["verification"]["remediation"]["current_question"]
    client.post("/api/tests/af-test/answers/submit", json={
        "question_id": rem_stored["id"],
        "option_id": rem_stored["correct_option_id"],
    })

    # Now answer Question 1 correctly
    res_q1 = client.post("/api/tests/af-test/answers/submit", json={
        "question_id": q1["id"],
        "option_id": q1["correct_option_id"],
    })
    assert res_q1.status_code == 200
    assert res_q1.json()["correct"] is True

    # Check overall test results
    prog = client.get("/api/tests/af-test/progress").json()
    assert prog["answered"] == 2
    assert prog["correct"] == 1
    assert prog["incorrect"] == 1
    assert prog["percentage"] == 50.0
    assert prog["status"] == "Completed"
    assert len(client.db["mathroot_answers"]) == 2


def test_parameter_space_exhaustion_handled_gracefully(client):
    questions = seed_af_test(client, ("easy",))
    enroll(client)
    q0 = questions[0]

    wrong_opt = next(o["id"] for o in q0["options"] if o["id"] != q0["correct_option_id"])
    client.post("/api/tests/af-test/answers/submit", json={"question_id": q0["id"], "option_id": wrong_opt})

    # Simulate that all 33 valid easy pairs have already been seen
    all_easy_pairs = manual.get_all_valid_parameters("easy")
    db_row = client.db["mathroot_answers"][0]
    db_row["verification"]["remediation"]["seen_params"] = [list(p) for p in all_easy_pairs]

    rem_stored = db_row["verification"]["remediation"]["current_question"]
    wrong_rem_opt = next(o["id"] for o in rem_stored["options"] if o["id"] != rem_stored["correct_option_id"])

    res = client.post("/api/tests/af-test/answers/submit", json={
        "question_id": rem_stored["id"],
        "option_id": wrong_rem_opt,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["remediation"]["status"] == "exhausted"
    assert data["remediation"]["question"] is None

    # Test can be finished without hang or infinite retry
    prog = client.get("/api/tests/af-test/progress").json()
    assert prog["status"] == "Completed"


def test_ai_remediation_generation_fallback_on_error(monkeypatch):
    monkeypatch.setattr(ai, "configuration", lambda: {"mode": "ollama"})

    def mock_ai_fail(difficulty, exclude_params=None):
        raise RuntimeError("AI model timeout")

    monkeypatch.setattr(ai, "generate_remediation_question", mock_ai_fail)

    topic = AlgebraicFractionsTopic()
    exclude = {(2, 1)}
    # When AI fails, topic should fall back to manual variation
    q = topic.generate_remediation_question("easy", exclude_params=exclude)
    manual.validate_question(q)
    _, params = manual.extract_question_parameters(q)
    assert params not in exclude


def test_ai_remediation_generation_rejects_duplicate_parameters(monkeypatch):
    monkeypatch.setattr(ai, "configuration", lambda: {"mode": "ollama"})

    # Suppose AI generates a question with parameters (3, 2)
    ai_q = manual.build_question_from_parameters("easy", (3, 2))
    monkeypatch.setattr(ai, "generate_question", lambda difficulty: ai_q)

    # Calling ai.generate_remediation_question with (3, 2) in exclude_params must raise ValueError
    with pytest.raises(ValueError, match="already used"):
        ai.generate_remediation_question("easy", exclude_params={(3, 2)})

    # Calling generator.generate_remediation_question falls back to manual and gives unseen params
    q = generator.generate_remediation_question("easy", exclude_params={(3, 2)})
    manual.validate_question(q)
    _, params = manual.extract_question_parameters(q)
    assert params != (3, 2)
