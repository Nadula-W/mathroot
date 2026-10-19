"""Supabase-backed teacher tests and student submissions. No SQLite.

All table queries use a server-only privileged Supabase client after verifying
Supabase Auth and checking roles/ownership in this module.
"""
import logging
import secrets
from dataclasses import asdict
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.contracts import Difficulty, InternalOption, InternalQuestion
from app.supabase_auth import (
    admin_client, current_user, require_student, require_teacher,
)
from app.topics import TOPICS
from app.topics.binomial import BinomialTopic

logger = logging.getLogger("uvicorn.error")
router = APIRouter(tags=["Supabase assessments"])


class CreateTest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    class_id: str = Field(min_length=1, max_length=64)
    topic_ids: list[str] = Field(min_length=1, max_length=5)
    questions_per_topic: int = Field(ge=1, le=10)
    difficulty: Difficulty = "easy"


class JoinClass(BaseModel):
    class_id: str = Field(min_length=1, max_length=64)
    join_code: str = Field(min_length=6, max_length=128)


class SubmitTestAnswer(BaseModel):
    question_id: str
    option_id: str


def first(table_name: str, column: str, value: str, columns: str = "*") -> dict | None:
    rows = (
        admin_client().table(table_name).select(columns)
        .eq(column, value).limit(1).execute().data
    ) or []
    return rows[0] if rows else None


def owned_class(class_id: str, teacher_id: str) -> dict:
    group = first("mathroot_classes", "id", class_id)
    if not group or group["teacher_id"] != teacher_id:
        raise HTTPException(403, "This class is not owned by your teacher account.")
    return group


def class_member(class_id: str, user: dict) -> None:
    if user["role"] == "teacher":
        owned_class(class_id, user["id"])
        return
    if user["requested_role"] == "teacher":
        raise HTTPException(403, "Teacher account is awaiting approval.")
    record = (
        admin_client().table("mathroot_class_members")
        .select("class_id")
        .eq("class_id", class_id).eq("student_id", user["id"])
        .limit(1).execute().data
    ) or []
    if not record:
        raise HTTPException(403, "Join this class before accessing its tests.")


def get_test_record(test_id: str) -> dict:
    test = first("mathroot_tests", "id", test_id)
    if not test:
        raise HTTPException(404, "Test not found.")
    return test


def public_detail(test: dict, include_questions: bool = False) -> dict:
    items = test["questions"]
    result = {
        "test_id": test["id"],
        "title": test["title"],
        "class_id": test["class_id"],
        "question_count": len(items),
        "topics": list(dict.fromkeys(item["topic_id"] for item in items)),
    }
    if include_questions:
        # Never expose correct_option_id, explanations, or misconception labels.
        result["questions"] = [
            {
                "question_id": item["id"],
                "topic_id": item["topic_id"],
                "difficulty": item["difficulty"],
                "statement": item["statement"],
                "options": [
                    {"id": option["id"], "text": option["text"]}
                    for option in item["options"]
                ],
            }
            for item in items
        ]
    return result


@router.post("/api/classes")
def create_class(
    teacher: Annotated[dict, Depends(require_teacher)],
    class_id: str = Query(min_length=1, max_length=64),
):
    class_id = class_id.strip()
    if not class_id:
        raise HTTPException(422, "Class ID is required.")
    existing = first("mathroot_classes", "id", class_id)
    if existing:
        if existing["teacher_id"] != teacher["id"]:
            raise HTTPException(409, "This class ID is already in use.")
        return {"class_id": class_id, "join_code": existing["join_code"]}
    try:
        row = (
            admin_client().table("mathroot_classes")
            .insert({
                "id": class_id,
                "teacher_id": teacher["id"],
                "join_code": secrets.token_urlsafe(16),
            }).execute().data[0]
        )
    except Exception as exc:
        raise HTTPException(409, "Class could not be created; try another ID.") from exc
    return {"class_id": row["id"], "join_code": row["join_code"]}


@router.get("/api/classes")
def teacher_classes(teacher: Annotated[dict, Depends(require_teacher)]):
    rows = (
        admin_client().table("mathroot_classes")
        .select("id,join_code,created_at")
        .eq("teacher_id", teacher["id"]).order("created_at", desc=True)
        .execute().data
    ) or []
    return [{"class_id": row["id"], "join_code": row["join_code"]} for row in rows]


@router.post("/api/classes/join")
def join_class(req: JoinClass, student: Annotated[dict, Depends(require_student)]):
    group = first("mathroot_classes", "id", req.class_id)
    if not group or not secrets.compare_digest(group["join_code"], req.join_code):
        raise HTTPException(403, "Invalid class ID or join code.")
    admin_client().table("mathroot_class_members").upsert(
        {"class_id": req.class_id, "student_id": student["id"]},
        on_conflict="class_id,student_id",
    ).execute()
    return {"status": "joined", "class_id": req.class_id}


@router.post("/api/tests")
def create_test(req: CreateTest, teacher: Annotated[dict, Depends(require_teacher)]):
    if len(set(req.topic_ids)) != len(req.topic_ids):
        raise HTTPException(422, "Select each topic only once.")
    missing = [topic_id for topic_id in req.topic_ids if topic_id not in TOPICS]
    if missing:
        raise HTTPException(422, f"Topics not ready: {', '.join(missing)}")
    if len(req.topic_ids) * req.questions_per_topic > 40:
        raise HTTPException(422, "Maximum 40 questions per test.")

    owned_class(req.class_id, teacher["id"])
    questions = []
    for topic_id in req.topic_ids:
        seen = set()
        manual = BinomialTopic() if topic_id == "binomial" else None
        for index in range(req.questions_per_topic):
            # Avoid multiplying model latency: first two per topic use Ollama,
            # remaining questions use the rule-based generator when available.
            generator = (
                TOPICS[topic_id]
                if manual is None or index < 2
                else manual
            )
            question = generator.generate_question(req.difficulty)
            if question.source_expression in seen and manual is not None:
                for _ in range(60):
                    alternative = manual.generate_question(req.difficulty)
                    if alternative.source_expression not in seen:
                        question = alternative
                        break
            if question.source_expression in seen:
                raise HTTPException(422, f"Not enough unique questions for {topic_id}.")
            seen.add(question.source_expression)
            questions.append(asdict(question))

    # One database insert persists the entire test and every question.
    test_id = str(uuid4())
    saved = (
        admin_client().table("mathroot_tests").insert({
            "id": test_id,
            "title": req.title.strip(),
            "class_id": req.class_id,
            "teacher_id": teacher["id"],
            "questions": questions,
        }).execute().data[0]
    )
    logger.info("MathRoot: saved %d questions to Supabase", len(questions))
    return public_detail(saved)


@router.get("/api/tests")
def list_tests(
    user: Annotated[dict, Depends(current_user)],
    class_id: str = Query(min_length=1, max_length=64),
):
    class_member(class_id, user)
    rows = (
        admin_client().table("mathroot_tests")
        .select("id,title,class_id,questions")
        .eq("class_id", class_id)
        .order("created_at", desc=True).execute().data
    ) or []
    return [public_detail(row) for row in rows]


@router.get("/api/tests/{test_id}")
def student_test(test_id: str, user: Annotated[dict, Depends(current_user)]):
    test = get_test_record(test_id)
    class_member(test["class_id"], user)
    return public_detail(test, include_questions=True)


@router.post("/api/tests/{test_id}/answers/submit")
def submit_test_answer(
    test_id: str,
    req: SubmitTestAnswer,
    student: Annotated[dict, Depends(require_student)],
):
    test = get_test_record(test_id)
    class_member(test["class_id"], student)
    data = next(
        (q for q in test["questions"] if q["id"] == req.question_id), None,
    )
    if data is None:
        raise HTTPException(404, "Question is not in this test.")
    option_data = next(
        (o for o in data["options"] if o["id"] == req.option_id), None,
    )
    if option_data is None:
        raise HTTPException(422, "Unknown answer option.")

    question = InternalQuestion(**{
        **data,
        "options": [InternalOption(**o) for o in data["options"]],
    })
    topic = TOPICS.get(question.topic_id)
    if not topic:
        raise HTTPException(422, "Topic module is unavailable.")

    correct = req.option_id == question.correct_option_id
    misconception = None if correct else option_data.get("misconception")
    try:
        admin_client().table("mathroot_answers").insert({
            "test_id": test_id,
            "question_id": req.question_id,
            "student_id": student["id"],
            "class_id": test["class_id"],
            "topic_id": question.topic_id,
            "option_id": req.option_id,
            "correct": correct,
            "misconception": misconception,
        }).execute()
    except Exception as exc:
        existing = (
            admin_client().table("mathroot_answers")
            .select("question_id")
            .eq("test_id", test_id).eq("question_id", req.question_id)
            .eq("student_id", student["id"]).limit(1).execute().data
        ) or []
        if existing:
            raise HTTPException(409, "You already answered this question.") from exc
        logger.exception("Failed saving MathRoot answer")
        raise HTTPException(503, "Could not save answer to Supabase.") from exc

    diagnosis = "none"
    if not correct:
        matches = (
            admin_client().table("mathroot_answers")
            .select("question_id")
            .eq("class_id", test["class_id"])
            .eq("student_id", student["id"])
            .eq("topic_id", question.topic_id)
            .eq("misconception", misconception)
            .execute().data
        ) or []
        diagnosis = "repeated_signal" if len(matches) >= 2 else "suspected"

    difficulties = ["easy", "medium", "hard"]
    current = difficulties.index(question.difficulty)
    next_level = (
        difficulties[min(2, current + 1)] if correct
        else difficulties[max(0, current - 1)]
    )
    right_option = next(
        o for o in question.options if o.id == question.correct_option_id
    )
    return {
        "correct": correct,
        "selected_option": option_data["text"],
        "correct_answer": right_option.text,
        "suspected_misconception": misconception,
        "diagnosis_status": diagnosis,
        "feedback": topic.feedback(question, misconception),
        "recommended_next_difficulty": next_level,
    }


@router.get("/api/tests/{test_id}/results")
def test_results(test_id: str, teacher: Annotated[dict, Depends(require_teacher)]):
    test = get_test_record(test_id)
    owned_class(test["class_id"], teacher["id"])
    rows = (
        admin_client().table("mathroot_answers")
        .select("student_id,topic_id,correct,misconception")
        .eq("test_id", test_id).execute().data
    ) or []

    topics, students = {}, {}
    for row in rows:
        topic_id, student_id = row["topic_id"], row["student_id"]
        t = topics.setdefault(topic_id, {
            "topic_id": topic_id, "answers": 0, "correct": 0, "misconceptions": {},
        })
        s = students.setdefault(student_id, {
            "student_id": student_id, "answered": 0, "correct": 0, "misconceptions": {},
        })
        t["answers"] += 1
        s["answered"] += 1
        t["correct"] += int(row["correct"])
        s["correct"] += int(row["correct"])
        code = row["misconception"]
        if code:
            for current in (t, s):
                current["misconceptions"][code] = current["misconceptions"].get(code, 0) + 1

    for t in topics.values():
        t["misconceptions"] = [
            {
                "code": code,
                "count": count,
                "recommendation": TOPICS[t["topic_id"]].teaching_recommendation(code),
            }
            for code, count in sorted(
                t["misconceptions"].items(), key=lambda item: -item[1]
            )
        ]
    for s in students.values():
        s["misconceptions"] = [
            {"code": code, "count": count}
            for code, count in s["misconceptions"].items()
        ]

    return {
        **public_detail(test),
        "student_count": len(students),
        "answers_submitted": len(rows),
        "topics_results": list(topics.values()),
        "students": sorted(students.values(), key=lambda s: s["student_id"]),
        "note": "Wrong-answer events suggest misconceptions; they do not prove them.",
    }


@router.get("/api/teacher/summary")
def teacher_summary(
    teacher: Annotated[dict, Depends(require_teacher)],
    class_id: str = Query(min_length=1, max_length=64),
    topic_id: str = "binomial",
):
    owned_class(class_id, teacher["id"])
    if topic_id not in TOPICS:
        raise HTTPException(422, "Topic module not available.")
    rows = (
        admin_client().table("mathroot_answers")
        .select("student_id,correct,misconception")
        .eq("class_id", class_id).eq("topic_id", topic_id)
        .execute().data
    ) or []
    counts = {}
    for row in rows:
        code = row["misconception"]
        if code:
            counts[code] = counts.get(code, 0) + 1
    signals = [
        {"code": code, "answer_count": count}
        for code, count in sorted(counts.items(), key=lambda x: -x[1])
    ]
    return {
        "class_id": class_id,
        "topic_id": topic_id,
        "total_answers": len(rows),
        "students": len({r["student_id"] for r in rows}),
        "correct_answers": sum(int(r["correct"]) for r in rows),
        "misconception_counts": signals,
        "recommendations": [
            {"code": s["code"], "action": TOPICS[topic_id].teaching_recommendation(s["code"])}
            for s in signals
        ],
        "note": "Incorrect-answer signals are not confirmed misconceptions.",
    }
