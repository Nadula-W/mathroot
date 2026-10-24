# assessments.py — code explained

**Source:** [backend/app/assessments.py](../../../backend/app/assessments.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Connects authenticated users, topic generation, shared answer verification and Supabase persistence. It implements the working class/test/answer/result routes.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–24: Code section

```python
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
from app.answer_verification import verify_answer
from app.topics import TOPICS
from app.topics.development.binomial.manual import BinomialTopic

logger = logging.getLogger("uvicorn.error")
router = APIRouter(tags=["Supabase assessments"])
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 27–43: answer_rows()

```python
def answer_rows(table="mathroot_answers", **filters):
    """Read all matching rows, including classes with more than one API page."""
    rows = []
    while True:
        query = admin_client().table(table).select("*")
        for key, value in filters.items():
            query = query.eq(key, value)
        keys = {
            "mathroot_answers": ("test_id", "question_id", "student_id"),
            "mathroot_class_members": ("class_id", "student_id"),
        }.get(table, ("id",))
        for key in keys:
            query = query.order(key)
        page = query.range(len(rows), len(rows) + 499).execute().data or []
        rows.extend(page)
        if len(page) < 500:
            return rows
```

**Explanation:**

- Builds equality filters, orders by stable key fields and reads 500-row pages until the final short page. rows collects every page so large class histories are not silently cut off.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Line 40: Requests an inclusive page starting at the number of rows already collected, with at most 500 rows.
- Line 42: A shorter page signals the end, so the helper returns all accumulated rows.

## Lines 46–56: progress()

```python
def progress(test, rows):
    """Derive status and scores solely from immutable persisted answers."""
    valid = {q["id"] for q in test["questions"]}
    rows = [r for r in rows if r["question_id"] in valid]
    total = len(valid)
    correct = sum(bool(r["correct"]) for r in rows)
    completed = bool(total) and len(rows) == total
    return {"answered": len(rows), "correct": correct, "incorrect": len(rows) - correct,
            "percentage": round(100 * correct / total, 1) if total else 0,
            "status": "Completed" if completed else "In Progress" if rows else "Not Started",
            "completed_at": max((r.get("created_at", "") for r in rows), default=None) if completed else None}
```

**Explanation:**

- Keeps answers belonging to saved question IDs, counts correct/incorrect answers and calculates percentage over the full test. All answered means Completed; some means In Progress. The latest answer timestamp becomes completion time.
- Line 48: Builds a set of saved question IDs; set lookup is used to ignore unrelated answers during scoring.
- Line 51: Counts persisted true correctness values. The frontend cannot increase this by changing React state.
- Line 52: An empty test is not considered complete; a nonempty test completes only when every saved question has an answer.
- Line 54: Converts the correct count to a percentage and avoids dividing by zero for an empty test.

## Lines 59–82: review()

```python
def review(test, student_id):
    rows = answer_rows(test_id=test["id"], student_id=student_id)
    history = answer_rows(class_id=test["class_id"], student_id=student_id)
    answers = []
    positions = {q["id"]: i for i, q in enumerate(test["questions"])}
    for row in sorted(rows, key=lambda r: positions.get(r["question_id"], len(positions))):
        data = next((q for q in test["questions"] if q["id"] == row["question_id"]), None)
        if not data:
            continue
        question = InternalQuestion(**{**data, "options": [InternalOption(**o) for o in data["options"]]})
        evidence = sum(r["topic_id"] == row["topic_id"] and r["misconception"] == row["misconception"] for r in history)
        levels = ["easy", "medium", "hard"]
        level = levels.index(data["difficulty"])
        detail = {"question_id": data["id"], "statement": data["statement"],
                        "option_id": row["option_id"], "correct": row["correct"],
                        "selected_option": next(o["text"] for o in data["options"] if o["id"] == row["option_id"]),
                        "correct_answer": next(o["text"] for o in data["options"] if o["id"] == data["correct_option_id"]),
                        "explanation": data["explanation"], "suspected_misconception": row["misconception"],
                        "diagnosis_status": "none" if row["correct"] else "repeated_signal" if evidence >= 2 else "suspected",
                        "recommended_next_difficulty": levels[min(2, level + 1) if row["correct"] else max(0, level - 1)],
                        "feedback": (TOPICS[data["topic_id"]].feedback(question, row["misconception"])
                                     if row["correct"] or row["misconception"] else "Incorrect answer. " + question.explanation)}
        # Old rows have no snapshot: retain deterministic review without invoking AI.
        snapshot = row.get("verification")
```

**Explanation:**

- Reads the student history, sorts answers into question order and reconstructs internal questions. Saved verification snapshots preserve accepted feedback; legacy answers use manual text without invoking AI again.
- Reuses the saved feedback snapshot for consistent review/retry; legacy rows without a snapshot use manual text.
- Line 63: Records each question's original test position, used to restore answer-review ordering.
- Line 69: Counts matching topic/misconception signals across saved class history. Repetition is still evidence, not proof of a diagnosis.
- Line 82: Reads the optional persisted feedback snapshot. get also works for historical rows lacking this field.

## Lines 83–94: review()

```python
        if snapshot:
            detail.update({k: snapshot[k] for k in (
                "feedback", "explanation", "corrective_guidance", "teaching_recommendation",
                "verification_method", "confidence",
            ) if k in snapshot})
        else:
            detail.update(verification_method="manual_fallback", confidence=None,
                          corrective_guidance=TOPICS[data["topic_id"]].teaching_recommendation(row["misconception"]) if row["misconception"] else "Review the worked solution.")
        if not row["correct"] and not row["misconception"]:
            detail["diagnosis_status"] = "unknown"
        answers.append(detail)
    return {**public_detail(test), **progress(test, rows), "answers": answers}
```

**Explanation:**

- Reads the student history, sorts answers into question order and reconstructs internal questions. Saved verification snapshots preserve accepted feedback; legacy answers use manual text without invoking AI again.
- Reuses the saved feedback snapshot for consistent review/retry; legacy rows without a snapshot use manual text.
- Line 92: A wrong answer without a supported misconception remains uncertain instead of inventing a diagnosis.

## Lines 97–105: student_classes()

```python
@router.get("/api/student/classes")
def student_classes(student: Annotated[dict, Depends(require_student)]):
    result = []
    for member in answer_rows("mathroot_class_members", student_id=student["id"]):
        group = first("mathroot_classes", "id", member["class_id"])
        if group:
            teacher = first("profiles", "id", group["teacher_id"], "full_name")
            result.append({"class_id": group["id"], "teacher_name": (teacher or {}).get("full_name")})
    return result
```

**Explanation:**

- Reads memberships for the verified student ID, then resolves class/teacher names. It returns no teacher join codes.
- FastAPI resolves the declared authentication dependencies before running the route body.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 108–116: student_results()

```python
@router.get("/api/student/results")
def student_results(student: Annotated[dict, Depends(require_student)]):
    result = []
    for group in student_classes(student):
        for test in answer_rows("mathroot_tests", class_id=group["class_id"]):
            state = progress(test, answer_rows(test_id=test["id"], student_id=student["id"]))
            if state["status"] == "Completed":
                result.append({**public_detail(test), **state})
    return sorted(result, key=lambda r: r["completed_at"] or "", reverse=True)
```

**Explanation:**

- Checks tests in joined classes, derives saved progress and returns completed results sorted by completion time.
- FastAPI resolves the declared authentication dependencies before running the route body.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 119–122: managed_tests()

```python
@router.get("/api/teacher/tests")
def managed_tests(teacher: Annotated[dict, Depends(require_teacher)]):
    return [{**public_detail(t), "participant_count": len({a["student_id"] for a in answer_rows(test_id=t["id"])})}
            for t in sorted(answer_rows("mathroot_tests", teacher_id=teacher["id"]), key=lambda t: t.get("created_at", ""), reverse=True)]
```

**Explanation:**

- Selects this teacher's tests and counts distinct participating students. public_detail strips hidden question data from summaries.
- FastAPI resolves the declared authentication dependencies before running the route body.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 125–133: delete_test()

```python
@router.delete("/api/tests/{test_id}")
def delete_test(test_id: str, teacher: Annotated[dict, Depends(require_teacher)]):
    test = get_test_record(test_id)
    owned_class(test["class_id"], teacher["id"])
    if test["teacher_id"] != teacher["id"]:
        raise HTTPException(403, "You do not own this test.")
    # Existing FK ON DELETE CASCADE removes answers in the same transaction.
    admin_client().table("mathroot_tests").delete().eq("id", test_id).eq("teacher_id", teacher["id"]).execute()
    return {"status": "deleted"}
```

**Explanation:**

- Checks class and test ownership before deleting this test. The existing answer foreign key cascades to its submissions; the class is retained.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Stops the success path with the specified HTTP error status and readable detail.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 136–140: saved_progress()

```python
@router.get("/api/tests/{test_id}/progress")
def saved_progress(test_id: str, student: Annotated[dict, Depends(require_student)]):
    test = get_test_record(test_id)
    class_member(test["class_id"], student)
    return review(test, student["id"])
```

**Explanation:**

- Checks membership and calls review for the authenticated student. A caller cannot supply another student identity in this URL.
- FastAPI resolves the declared authentication dependencies before running the route body.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 143–147: student_review()

```python
@router.get("/api/tests/{test_id}/students/{student_id}")
def student_review(test_id: str, student_id: str, teacher: Annotated[dict, Depends(require_teacher)]):
    test = get_test_record(test_id)
    owned_test(test, teacher["id"])
    return review(test, student_id)
```

**Explanation:**

- Checks teacher ownership before returning the selected student's saved answers for this test.
- FastAPI resolves the declared authentication dependencies before running the route body.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 150–155: CreateTest

```python
class CreateTest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    class_id: str = Field(min_length=1, max_length=64)
    topic_ids: list[str] = Field(min_length=1, max_length=5)
    questions_per_topic: int = Field(ge=1, le=10)
    difficulty: Difficulty = "easy"
```

**Explanation:**

- The active API input schema. Pydantic checks its fields/constraints before the route body. The student identity is obtained from authentication, not from this JSON.
- Pydantic checks these declared lengths, ranges or counts before route logic uses the input.

## Lines 158–160: JoinClass

```python
class JoinClass(BaseModel):
    class_id: str = Field(min_length=1, max_length=64)
    join_code: str = Field(min_length=1, max_length=128)
```

**Explanation:**

- The active API input schema. Pydantic checks its fields/constraints before the route body. The student identity is obtained from authentication, not from this JSON.
- Pydantic checks these declared lengths, ranges or counts before route logic uses the input.

## Lines 163–165: SubmitTestAnswer

```python
class SubmitTestAnswer(BaseModel):
    question_id: str
    option_id: str
```

**Explanation:**

- The active API input schema. Pydantic checks its fields/constraints before the route body. The student identity is obtained from authentication, not from this JSON.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 168–173: first()

```python
def first(table_name: str, column: str, value: str, columns: str = "*") -> dict | None:
    rows = (
        admin_client().table(table_name).select(columns)
        .eq(column, value).limit(1).execute().data
    ) or []
    return rows[0] if rows else None
```

**Explanation:**

- Returns at most one matching database row, or None when there is no match.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.

## Lines 176–180: owned_class()

```python
def owned_class(class_id: str, teacher_id: str) -> dict:
    group = first("mathroot_classes", "id", class_id)
    if not group or group["teacher_id"] != teacher_id:
        raise HTTPException(403, "This class is not owned by your teacher account.")
    return group
```

**Explanation:**

- Compares the saved teacher_id with the verified teacher. Missing or foreign classes raise 403.
- Stops the success path with the specified HTTP error status and readable detail.

## Lines 183–186: owned_test()

```python
def owned_test(test: dict, teacher_id: str) -> None:
    owned_class(test["class_id"], teacher_id)
    if test["teacher_id"] != teacher_id:
        raise HTTPException(403, "You do not own this test.")
```

**Explanation:**

- Checks both class ownership and the test's own teacher_id before protected teacher access.
- Stops the success path with the specified HTTP error status and readable detail.

## Lines 189–202: class_member()

```python
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
```

**Explanation:**

- An approved teacher must own the class. Students need a matching student/class membership row. A copied test URL does not grant membership.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Stops the success path with the specified HTTP error status and readable detail.

## Lines 205–209: get_test_record()

```python
def get_test_record(test_id: str) -> dict:
    test = first("mathroot_tests", "id", test_id)
    if not test:
        raise HTTPException(404, "Test not found.")
    return test
```

**Explanation:**

- Looks up the saved test and returns 404 when it does not exist.
- Stops the success path with the specified HTTP error status and readable detail.

## Lines 212–235: public_detail()

```python
def public_detail(test: dict, include_questions: bool = False) -> dict:
    items = test["questions"]
    result = {
        "test_id": test["id"],
        "title": test["title"],
        "class_id": test["class_id"],
        "question_count": len(items),
        "topics": list(dict.fromkeys(item["topic_id"] for item in items)),
        "difficulty": ", ".join(dict.fromkeys(item["difficulty"] for item in items)),
        "created_at": test.get("created_at"),
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
```

**Explanation:**

- Builds safe summaries/questions without correct_option_id, explanations or misconception labels. Hidden data stays server-side until the relevant answer is submitted.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 236–238: public_detail()

```python
            for item in items
        ]
    return result
```

**Explanation:**

- Builds safe summaries/questions without correct_option_id, explanations or misconception labels. Hidden data stays server-side until the relevant answer is submitted.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 241–265: create_class()

```python
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
```

**Explanation:**

- Trims the requested ID, handles ownership/conflicts and creates a random join code for a new teacher-owned class. An owner can retrieve their existing code.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Stops the success path with the specified HTTP error status and readable detail.
- Generates a hard-to-guess join code; knowing a class ID alone does not authorize joining.
- The decorator connects this HTTP method/path to the following Python route function.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.

## Lines 268–276: teacher_classes()

```python
@router.get("/api/classes")
def teacher_classes(teacher: Annotated[dict, Depends(require_teacher)]):
    rows = (
        admin_client().table("mathroot_classes")
        .select("id,join_code,created_at")
        .eq("teacher_id", teacher["id"]).order("created_at", desc=True)
        .execute().data
    ) or []
    return [{"class_id": row["id"], "join_code": row["join_code"]} for row in rows]
```

**Explanation:**

- Reads class IDs and join codes filtered to the approved teacher ID.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 279–294: join_class()

```python
@router.post("/api/classes/join")
def join_class(req: JoinClass, student: Annotated[dict, Depends(require_student)]):
    req.class_id = req.class_id.strip()
    group = first("mathroot_classes", "id", req.class_id)
    if not group:
        raise HTTPException(404, "Class ID does not exist.")
    existing = answer_rows("mathroot_class_members", class_id=req.class_id, student_id=student["id"])
    if existing:
        return {"status": "already_enrolled", "class_id": req.class_id}
    if not secrets.compare_digest(group["join_code"], req.join_code.strip()):
        raise HTTPException(403, "Incorrect class join code.")
    admin_client().table("mathroot_class_members").upsert(
        {"class_id": req.class_id, "student_id": student["id"]},
        on_conflict="class_id,student_id",
    ).execute()
    return {"status": "joined", "class_id": req.class_id}
```

**Explanation:**

- Checks existence, handles already-enrolled students, securely compares the join code and upserts membership under the verified student ID.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Stops the success path with the specified HTTP error status and readable detail.
- Compares the submitted join code with the saved code before creating membership.
- The decorator connects this HTTP method/path to the following Python route function.
- Line 285: Checks for an existing saved record before trying to insert a duplicate submission or membership.

## Lines 297–309: create_test()

```python
@router.post("/api/tests")
def create_test(req: CreateTest, teacher: Annotated[dict, Depends(require_teacher)]):
    req.title = req.title.strip()
    req.class_id = req.class_id.strip()
    if len(req.title) < 3:
        raise HTTPException(422, "Test title must contain at least three characters.")
    if len(set(req.topic_ids)) != len(req.topic_ids):
        raise HTTPException(422, "Select each topic only once.")
    missing = [topic_id for topic_id in req.topic_ids if topic_id not in TOPICS]
    if missing:
        raise HTTPException(422, f"Topics not ready: {', '.join(missing)}")
    if len(req.topic_ids) * req.questions_per_topic > 40:
        raise HTTPException(422, "Maximum 40 questions per test.")
```

**Explanation:**

- Checks topic choices, limits and class ownership. It generates unique questions, converts dataclasses to dictionaries and inserts the complete question list into one test record.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Stops the success path with the specified HTTP error status and readable detail.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 311–329: create_test()

```python
    owned_class(req.class_id, teacher["id"])
    questions = []
    for topic_id in req.topic_ids:
        seen = set()
        manual = BinomialTopic() if topic_id == "binomial" else None
        for _ in range(req.questions_per_topic):
            # The configured topic owns Ollama generation and its safe fallback.
            generator = TOPICS[topic_id]
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
```

**Explanation:**

- Checks topic choices, limits and class ownership. It generates unique questions, converts dataclasses to dictionaries and inserts the complete question list into one test record.
- Stops the success path with the specified HTTP error status and readable detail.
- Line 328: Records this mathematical expression to prevent duplicate questions within the generated topic section.
- Line 329: Converts the immutable question dataclass into nested dictionaries suitable for JSON storage.

## Lines 331–343: create_test()

```python
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
```

**Explanation:**

- Checks topic choices, limits and class ownership. It generates unique questions, converts dataclasses to dictionaries and inserts the complete question list into one test record.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Creates opaque IDs so option identifiers do not reveal correctness/misconception semantics.

## Lines 346–358: list_tests()

```python
@router.get("/api/tests")
def list_tests(
    user: Annotated[dict, Depends(current_user)],
    class_id: str = Query(min_length=1, max_length=64),
):
    class_member(class_id, user)
    rows = (
        admin_client().table("mathroot_tests")
        .select("id,title,class_id,questions,created_at")
        .eq("class_id", class_id)
        .order("created_at", desc=True).execute().data
    ) or []
    return [{**public_detail(row), **progress(row, answer_rows("mathroot_answers", test_id=row["id"], student_id=user["id"]))} for row in rows]
```

**Explanation:**

- Checks class access and combines each safe saved-test summary with progress from this user's saved answers.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 361–365: student_test()

```python
@router.get("/api/tests/{test_id}")
def student_test(test_id: str, user: Annotated[dict, Depends(current_user)]):
    test = get_test_record(test_id)
    class_member(test["class_id"], user)
    return public_detail(test, include_questions=True)
```

**Explanation:**

- Loads a test, verifies class access and returns safe questions through public_detail.
- FastAPI resolves the declared authentication dependencies before running the route body.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 368–388: submit_test_answer()

```python
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
    existing = answer_rows(test_id=test_id, question_id=req.question_id, student_id=student["id"])
    if existing:
        return next(a for a in review(test, student["id"])["answers"] if a["question_id"] == req.question_id)
```

**Explanation:**

- Checks membership and that question/option belong to the test. Existing answers return immediately. Otherwise it invokes shared verification, inserts verified fields/snapshot and returns review. A unique-key race also returns the original saved answer.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Stops the success path with the specified HTTP error status and readable detail.
- The decorator connects this HTTP method/path to the following Python route function.
- Line 386: Checks for an existing saved record before trying to insert a duplicate submission or membership.

## Lines 390–413: submit_test_answer()

```python
    question = InternalQuestion(**{
        **data,
        "options": [InternalOption(**o) for o in data["options"]],
    })
    topic = TOPICS.get(question.topic_id)
    if not topic:
        raise HTTPException(422, "Topic module is unavailable.")

    verification = verify_answer(question, req.option_id, topic)
    correct = verification["correct"]
    misconception = verification["suspected_misconception"]
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
            "verification": verification,
        }).execute()
    except Exception as exc:
```

**Explanation:**

- Checks membership and that question/option belong to the test. Existing answers return immediately. Otherwise it invokes shared verification, inserts verified fields/snapshot and returns review. A unique-key race also returns the original saved answer.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Stops the success path with the specified HTTP error status and readable detail.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- Line 398: Delegates grading/feedback to the existing shared service using the server-loaded question and selected option.
- Line 411: Persists the accepted feedback together with the answer so future views and retries remain consistent.

## Lines 414–425: submit_test_answer()

```python
        existing = (
            admin_client().table("mathroot_answers")
            .select("question_id")
            .eq("test_id", test_id).eq("question_id", req.question_id)
            .eq("student_id", student["id"]).limit(1).execute().data
        ) or []
        if existing:
            return next(a for a in review(test, student["id"])["answers"] if a["question_id"] == req.question_id)
        logger.exception("Failed saving MathRoot answer")
        raise HTTPException(503, "Could not save answer to Supabase.") from exc

    return next(a for a in review(test, student["id"])["answers"] if a["question_id"] == req.question_id)
```

**Explanation:**

- Checks membership and that question/option belong to the test. Existing answers return immediately. Otherwise it invokes shared verification, inserts verified fields/snapshot and returns review. A unique-key race also returns the original saved answer.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Stops the success path with the specified HTTP error status and readable detail.

## Lines 428–450: test_results()

```python
@router.get("/api/tests/{test_id}/results")
def test_results(test_id: str, teacher: Annotated[dict, Depends(require_teacher)]):
    test = get_test_record(test_id)
    owned_test(test, teacher["id"])
    rows = answer_rows(test_id=test_id)

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
```

**Explanation:**

- Tests that results. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- FastAPI resolves the declared authentication dependencies before running the route body.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 452–470: test_results()

```python
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
        profile = first("profiles", "id", s["student_id"], "full_name")
        s["full_name"] = (profile or {}).get("full_name") or "Student"
        s.update(progress(test, answer_rows(test_id=test_id, student_id=s["student_id"])))
        s["misconceptions"] = [
            {"code": code, "count": count}
            for code, count in s["misconceptions"].items()
        ]
```

**Explanation:**

- Tests that results. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 472–485: test_results()

```python
    scores = [s["percentage"] for s in students.values() if s["status"] == "Completed"]
    return {
        **public_detail(test),
        "enrolled_count": len(answer_rows("mathroot_class_members", class_id=test["class_id"])),
        "completed_count": len(scores),
        "average_score": round(sum(scores) / len(scores), 1) if scores else None,
        "highest_score": max(scores) if scores else None,
        "lowest_score": min(scores) if scores else None,
        "student_count": len(students),
        "answers_submitted": len(rows),
        "topics_results": list(topics.values()),
        "students": sorted(students.values(), key=lambda s: s["student_id"]),
        "note": "Wrong-answer events suggest misconceptions; they do not prove them.",
    }
```

**Explanation:**

- Tests that results. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Line 472: Includes only completed students when calculating class average/highest/lowest values.

## Lines 488–511: teacher_summary()

```python
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
```

**Explanation:**

- Counts answer correctness and misconception codes for an owned class/topic and returns topic-specific teaching actions.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Stops the success path with the specified HTTP error status and readable detail.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 512–524: teacher_summary()

```python
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
```

**Explanation:**

- Counts answer correctness and misconception codes for an owned class/topic and returns topic-specific teaching actions.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Connected files

Follow these imports to their matching code explanations:

- [app/answer_verification.py](answer_verification.py.md)
- [app/contracts.py](contracts.py.md)
- [app/supabase_auth.py](supabase_auth.py.md)
- [app/topics/__init__.py](topics/__init__.py.md)
- [app/topics/development/binomial/manual.py](topics/development/binomial/manual.py.md)

## How to explain this file in the viva

“Connects authenticated users, topic generation, shared answer verification and Supabase persistence. It implements the working class/test/answer/result routes.”
