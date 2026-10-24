# REST API for MathRoot student and teacher interfaces

Open `http://127.0.0.1:8000/docs` for the current FastAPI schema. Browser assessment requests use `/backend/api/...`; Next.js forwards them to FastAPI's `/api/...` routes.

## Authentication and access

Assessment requests require `Authorization: Bearer <Supabase access token>`. `frontend/lib/backend-api.ts` adds it from the current session. FastAPI verifies the user and checks approved role, class membership or teacher ownership. Student identity and grades are never accepted from form fields. Login/registration communicate with Supabase Auth directly.

## Topics and service status

| Method and URL | Result |
| --- | --- |
| `GET /health` | Backend process status; not a database connectivity test. |
| `GET /api/topics` | Topic IDs, names, owners and readiness; only `binomial` is ready. |
| `GET /api/ai/status` | Local Ollama/model availability for the existing Binomial provider. |

## Classes

| Method and URL | Access and behaviour |
| --- | --- |
| `POST /api/classes?class_id=class-001` | Teacher creates a class or retrieves their existing class/join code. |
| `GET /api/classes` | Teacher's owned classes and join codes. |
| `POST /api/classes/join` | Student joins with `{"class_id":"class-001","join_code":"..."}`. |
| `GET /api/student/classes` | Student's saved memberships. |

## Test creation and listings

`POST /api/tests` requires an owning teacher:

```json
{
  "title": "Distribution practice",
  "class_id": "class-001",
  "topic_ids": ["binomial"],
  "questions_per_topic": 5,
  "difficulty": "easy"
}
```

The backend generates the test once, mathematically validates questions, and stores the canonical question array in `mathroot_tests`.

| Method and URL | Result |
| --- | --- |
| `GET /api/tests?class_id=class-001` | Accessible class tests, with the student's saved progress where appropriate. |
| `GET /api/teacher/tests` | Teacher's owned tests and participation counts. |
| `GET /api/tests/{test_id}` | Test details and safe questions after class-access checks. |
| `DELETE /api/tests/{test_id}` | Owning teacher deletes a test; the configured foreign key cascades its answers. |

## Public questions and bilingual presentation

The existing canonical fields stay English. A question's response can additionally contain a `translations.si` map and `translation_warnings` listing text fields without a safe Sinhala translation. The following is illustrative; real IDs are opaque UUIDs:

```json
{
  "question_id": "<question UUID>",
  "topic_id": "binomial",
  "difficulty": "easy",
  "statement": "Expand and simplify: 3(x + 4)",
  "options": [
    {"id": "<A UUID>", "text": "3x + 12"},
    {"id": "<B UUID>", "text": "3x + 4"},
    {"id": "<C UUID>", "text": "x + 12"},
    {"id": "<D UUID>", "text": "3x - 12"}
  ],
  "translations": {
    "si": {"statement": "ප්‍රසාරණය කර සුළු කරන්න: 3(x + 4)"}
  },
  "translation_warnings": []
}
```

Only display text receives translation metadata. Option IDs/order and algebraic text stay intact. Correct keys, explanations and misconception mappings are withheld from unanswered questions. There is **no language query/body parameter**: one response supplies both displays, so switching languages does not regenerate or refetch a test.

Reviewed topic templates are preferred. Unknown prose may use a topic's optional translation provider; unsafe or unavailable translations retain English and report missing fields. These metadata additions are response-only: no language column, migration, duplicated test or historical rewrite is required.

## Answer submission and saved progress

`POST /api/tests/{test_id}/answers/submit` requires an enrolled student:

```json
{"question_id":"<question UUID>","option_id":"<chosen option UUID>"}
```

The backend checks the option against the saved key, obtains validated AI feedback or manual fallback, and saves one immutable answer. Retrying returns the original saved result, including concurrent duplicate submissions; it does not award another mark. Results contain canonical feedback and optional Sinhala display metadata for supported statement/explanation/feedback/guidance fields. AI feedback validation is performed before presentation translation.

| Method and URL | Result |
| --- | --- |
| `GET /api/tests/{test_id}/progress` | Student's saved answers, score and completion status. |
| `GET /api/student/results` | Student's completed test results. |
| `GET /api/tests/{test_id}/students/{student_id}` | Owning teacher's view of one student's saved result. |

Old answer rows without a verification snapshot retain their deterministic review path. Reviewed Binomial wording can receive Sinhala presentation on read; unknown legacy prose remains English with a warning. No answer is regraded.

## Teacher results and recommendations

| Method and URL | Result |
| --- | --- |
| `GET /api/tests/{test_id}/results` | Owning teacher's student/topic performance and misconception summary. |
| `GET /api/teacher/summary?class_id=class-001&topic_id=binomial` | Owning teacher's class-level signals and interventions. |

Topic names, statuses and stable misconception codes are localized in the frontend dictionary. Supported teaching action/recommendation text also carries backend presentation metadata. Scores and aggregation continue using canonical IDs/codes.

## Errors and current limits

- `401`: missing/invalid login; `403`: wrong role or class/ownership access.
- `404`: missing record; `422`: invalid request; `503`: temporary upstream network failure.
- Fixed API errors are displayed through the frontend's reviewed message map. Unrecognized provider/server text is retained rather than inventing a translation.
- Current submissions are MCQs. Free-text answers, the four unfinished topics and adaptive diagnosis beyond the existing signals are not enabled.
- Earlier standalone `/api/questions/generate`, `/api/answers/submit` and `/api/practice/next` demo routes are not the current assessment workflow. Storage is Supabase PostgreSQL, not SQLite.
