
"""Teacher-created Mathematics tests. Local development version."""

import json
from dataclasses import asdict
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app import storage
from app.contracts import Difficulty
from app.topics import TOPICS

router = APIRouter(prefix="/api/tests", tags=["Teacher tests"])

#Defines the information a teacher must provide to generate a test.
class CreateTest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    class_id: str = Field(min_length=1, max_length=64)
    topic_ids: list[str] = Field(min_length=1, max_length=5)
    questions_per_topic: int = Field(ge=1, le=10)
    difficulty: Difficulty = "easy"


def initialize():
    with storage.db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                class_id TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_questions (
                test_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                PRIMARY KEY (test_id, question_id),
                UNIQUE(test_id, position)
            )
        """)


def test_detail(test_id: str, include_questions=False):
    with storage.db() as conn:
        test = conn.execute(
            "SELECT * FROM tests WHERE id = ?",
            (test_id,)
        ).fetchone()

        if test is None:
            raise HTTPException(404, "Test not found.")

        rows = conn.execute("""
            SELECT q.data
            FROM test_questions tq
            JOIN questions q ON q.id = tq.question_id
            WHERE tq.test_id = ?
            ORDER BY tq.position
        """, (test_id,)).fetchall()

    items = [json.loads(row["data"]) for row in rows]

    result = {
        "test_id": test_id,
        "title": test["title"],
        "class_id": test["class_id"],
        "question_count": len(items),
        "topics": list(dict.fromkeys(
            item["topic_id"] for item in items
        )),
    }

    if include_questions:
        result["questions"] = [
            {
                "question_id": item["id"],
                "topic_id": item["topic_id"],
                "difficulty": item["difficulty"],
                "statement": item["statement"],
                "options": [
                    {"id": o["id"], "text": o["text"]}
                    for o in item["options"]
                ],
            }
            for item in items
        ]

    return result


@router.post("")
def create_test(req: CreateTest):

    if len(req.topic_ids) != len(set(req.topic_ids)):
        raise HTTPException(422, "Select each topic only once.")

    missing = [
        topic_id for topic_id in req.topic_ids
        if topic_id not in TOPICS
    ]

    if missing:
        raise HTTPException(
            422, f"Topics not ready: {', '.join(missing)}"
        )

    if len(req.topic_ids) * req.questions_per_topic > 40:
        raise HTTPException(422, "Maximum 40 questions per test.")

    # Create unique questions before saving the test.
    questions = []

    for topic_id in req.topic_ids:
        seen = set()

        for _ in range(req.questions_per_topic):
            for attempt in range(40):
                question = TOPICS[topic_id].generate_question(
                    req.difficulty
                )

                if question.source_expression not in seen:
                    seen.add(question.source_expression)
                    questions.append(question)
                    break
            else:
                raise HTTPException(
                    422,
                    f"Could not produce unique questions for {topic_id}."
                )

    test_id = str(uuid4())

    # Save the test and all questions in one transaction.
    with storage.db() as conn:
        conn.execute(
            "INSERT INTO tests (id, title, class_id) VALUES (?, ?, ?)",
            (test_id, req.title.strip(), req.class_id)
        )

        for position, question in enumerate(questions, 1):
            conn.execute("""
                INSERT INTO questions
                (id, class_id, topic_id, difficulty, data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                question.id,
                req.class_id,
                question.topic_id,
                question.difficulty,
                json.dumps(asdict(question)),
            ))

            conn.execute("""
                INSERT INTO test_questions
                (test_id, question_id, position)
                VALUES (?, ?, ?)
            """, (test_id, question.id, position))

    return test_detail(test_id)


@router.get("")
def list_tests(
    class_id: str = Query(min_length=1, max_length=64)
):
    with storage.db() as conn:
        rows = conn.execute("""
            SELECT id FROM tests
            WHERE class_id = ?
            ORDER BY created_at DESC, rowid DESC
        """, (class_id,)).fetchall()

    return [test_detail(row["id"]) for row in rows]


@router.get("/{test_id}")
def student_test(test_id: str):
    return test_detail(test_id, include_questions=True)


@router.get("/{test_id}/results")
def test_results(test_id: str):
    detail = test_detail(test_id)

    with storage.db() as conn:
        rows = conn.execute("""
            SELECT q.topic_id, a.student_id,
                   a.correct, a.misconception
            FROM test_questions tq
            JOIN questions q ON q.id = tq.question_id
            JOIN answers a ON a.question_id = tq.question_id
            WHERE tq.test_id = ?
        """, (test_id,)).fetchall()

    topics = {}
    students = {}

    for row in rows:
        topic_id = row["topic_id"]
        student_id = row["student_id"]

        t = topics.setdefault(topic_id, {
            "topic_id": topic_id,
            "answers": 0,
            "correct": 0,
            "misconceptions": {},
        })

        t["answers"] += 1
        t["correct"] += row["correct"]

        s = students.setdefault(student_id, {
            "student_id": student_id,
            "answered": 0,
            "correct": 0,
            "misconceptions": {},
        })

        s["answered"] += 1
        s["correct"] += row["correct"]

        if row["misconception"]:
            code = row["misconception"]

            t["misconceptions"][code] = (
                t["misconceptions"].get(code, 0) + 1
            )

            s["misconceptions"][code] = (
                s["misconceptions"].get(code, 0) + 1
            )

    for t in topics.values():
        t["misconceptions"] = [
            {
                "code": code,
                "count": count,
                "recommendation": (
                    TOPICS[t["topic_id"]].teaching_recommendation(code)
                ),
            }
            for code, count in sorted(
                t["misconceptions"].items(),
                key=lambda item: -item[1]
            )
        ]

    for s in students.values():
        s["misconceptions"] = [
            {"code": code, "count": count}
            for code, count in s["misconceptions"].items()
        ]

    return {
        **detail,
        "student_count": len(students),
        "answers_submitted": len(rows),
        "topics_results": list(topics.values()),
        "students": sorted(
            students.values(),
            key=lambda item: item["student_id"]
        ),
        "note": (
            "Error counts are answer events "
            "and do not prove a misconception."
        ),
    }
