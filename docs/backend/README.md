# Backend — what it does and how it connects

**For code-by-code explanations, open the [matching source-file index](SOURCE_INDEX.md).** Each source file now has its own Markdown explanation with actual code blocks. This page remains the overview.

[Back to the viva guide](../README.md) · [Frontend guide](../frontend/README.md)

The backend receives requests, checks permissions, generates questions, grades answers and saves results. **FastAPI** defines URLs; **Pydantic** checks input/output shapes; **SymPy** checks mathematics; **Ollama** provides AI assistance; **Supabase** stores accounts and assessment data.

## 1. Read these source files first

Paths below are relative to `backend/`.

| Source file | Main code and purpose |
| --- | --- |
| [app/main.py](../../backend/app/main.py) | Creates the FastAPI `app` and includes the assessment router. `health()` reports that the server is running, `topics()` lists planned topics, and `ai_status()` checks Ollama availability. The network-error handler returns a readable 503. `/health` does not actually query the database. |
| [app/contracts.py](../../backend/app/contracts.py) | Shared data shapes. `InternalOption` holds an option ID/text/misconception; `InternalQuestion` also holds the hidden key, explanation and mathematical expressions. `Difficulty` restricts difficulty names. Public question models omit hidden data. Some request models, such as `AnswerRequest` with a manual student ID, are older contracts; the active assessment route uses its own models and verified identity. |
| [app/supabase_auth.py](../../backend/app/supabase_auth.py) | `current_user()` verifies the bearer token with Supabase and loads the profile. `require_teacher()` and `require_student()` restrict roles. `public_client()` handles token verification; `admin_client()` uses the backend-only secret for database operations. Clients are cached for reuse, and `client_options()` configures pooled HTTP/1.1 connections. |
| [app/assessments.py](../../backend/app/assessments.py) | Main class/test/result routes, request models and authorization helpers. It connects authentication, topic modules, verification and database persistence. Details below. |
| [app/answer_verification.py](../../backend/app/answer_verification.py) | Shared answer grading and AI/manual feedback. It does not generate questions. Details below. |
| [app/safe_symbolic.py](../../backend/app/safe_symbolic.py) | `parse_math()` accepts a small, bounded arithmetic syntax and builds SymPy objects. Its inner `convert()` rejects unsupported syntax. `equivalent()` compares expressions using `cancel`. Prepared for future free-text answers; current MCQ submissions do not call it. |
| [app/topics/base.py](../../backend/app/topics/base.py) | `TopicModule` describes the common methods: generate a question, return student feedback, and recommend a teaching action. A Python `Protocol` describes expected methods without forcing inheritance. |
| [app/topics/__init__.py](../../backend/app/topics/__init__.py) | `TOPICS` maps ready topic IDs to generator objects. `PLANNED_TOPICS` supplies display names, owners and readiness. Only Binomial is registered and ready. |

## 2. How assessments.py works

The input models are `CreateTest`, `JoinClass` and `SubmitTestAnswer`. They validate lengths/counts and expected fields before the route runs. `Depends(...)` tells FastAPI to run the required authentication function first.

| Helpers | Job |
| --- | --- |
| `answer_rows()` / `first()` | Read matching database rows. The first helper reads in pages so large lists are not silently cut off. |
| `owned_class()` / `owned_test()` | Check teacher ownership. |
| `class_member()` | Check student enrollment, or owning-teacher access. A test link alone does not grant access. |
| `get_test_record()` | Load the test or raise 404. |
| `public_detail()` | Build safe summaries/questions without revealing correct options or explanations. |
| `progress()` | Count saved answers and derive score/status. All questions answered means Completed; some means In Progress. |
| `review()` | Build submitted-answer feedback from stored snapshots. Older answers use deterministic feedback without another AI request. |

These are the implemented assessment endpoints, without the frontend's `/backend` prefix:

| Method and URL | Route function and purpose |
| --- | --- |
| `POST /api/classes?class_id=...` | `create_class()` creates an owned class and random join code, or retrieves the owner's existing code. |
| `GET /api/classes` | `teacher_classes()` lists the teacher's classes/codes. |
| `POST /api/classes/join` | `join_class()` checks class ID/code and persistently enrolls the authenticated student. |
| `GET /api/student/classes` | `student_classes()` lists that student's memberships and available teacher names. |
| `POST /api/tests` | `create_test()` checks class ownership, calls registered topic generators and saves the questions in one test record. |
| `GET /api/tests?class_id=...` | `list_tests()` checks access and returns test summaries with the user's saved progress. |
| `GET /api/tests/{test_id}` | `student_test()` returns safe test questions after checking class access. |
| `POST /api/tests/{test_id}/answers/submit` | `submit_test_answer()` validates question/option, returns an existing answer on retry, or verifies and saves a new answer. |
| `GET /api/tests/{test_id}/progress` | `saved_progress()` returns the enrolled student's own saved review/progress. |
| `GET /api/student/results` | `student_results()` lists that student's completed tests in joined classes. |
| `GET /api/teacher/tests` | `managed_tests()` lists owned tests and participant counts. |
| `GET /api/tests/{test_id}/results` | `test_results()` builds the owning teacher's class/student/misconception summary. |
| `GET /api/tests/{test_id}/students/{student_id}` | `student_review()` lets the owning teacher inspect one student's saved answers. |
| `GET /api/teacher/summary?class_id=...` | `teacher_summary()` aggregates class-wide signals for a topic. |
| `DELETE /api/tests/{test_id}` | `delete_test()` checks ownership and deletes the test. Its database foreign key also deletes that test's answers. |

## 3. What AI does, and what decides correctness

In [answer_verification.py](../../backend/app/answer_verification.py):

- `Analysis` defines validated feedback: proposed grade, explanation, possible misconception, confidence and correction.
- `FeedbackSelection` is a smaller Ollama response. It selects approved explanation/tip indices instead of inventing mathematical prose.
- `FeedbackProvider` describes the `analyze(context)` method for any provider.
- `OllamaFeedbackProvider.analyze()` sends question-only context to local Ollama, parses structured JSON and converts the selections to `Analysis`.
- `setting()` reads bounded numeric environment settings with safe defaults.
- `verify_answer()` grades by the stored correct option ID, prepares manual feedback, then optionally attempts AI analysis. A topic's optional `answer_feedback_provider()` can select its own provider. Invalid, contradictory, low-confidence or failed AI output keeps the manual result.

**The LLM does not decide the final score.** SymPy validates generated mathematics; option-ID comparison grades the MCQ. AI diagnoses are limited to supported distractor evidence and approved explanations. No name, access token or database secret belongs in the AI context.

## 4. Working Binomial source files

| Source file | Main functions and connection |
| --- | --- |
| [binomial/manual.py](../../backend/app/topics/development/binomial/manual.py) | `_as_text()` formats algebra. `BinomialTopic.generate_question()` chooses coefficients, calculates the answer with SymPy, constructs diagnostic wrong answers, checks uniqueness/equivalence and assigns opaque UUIDs. `feedback()` explains a possible mistake; `teaching_recommendation()` suggests practice; `verification_feedback()` supplies trusted alternative feedback for shared AI selection. |
| [binomial/generator.py](../../backend/app/topics/development/binomial/generator.py) | `generator_mode()` reads auto/manual mode, `selected_model()` chooses the local model, and `llm_status()` checks availability. `LLMBinomialTopic` extends the manual class. Its `generate_question()` tries `_generate_using_ollama()` and falls back on failure. Ollama proposes integer coefficients; Python/SymPy computes and verifies the answers independently. |
| [binomial/__init__.py](../../backend/app/topics/development/binomial/__init__.py) | Exposes the manual class/helper from this package. It contains no grading logic. |

Example: for `3(x + 4)`, the correct result is `3x + 12`. Selecting `3x + 4` may indicate `DISTRIBUTION_CONSTANT`: the constant was not multiplied. That is evidence of a possible misconception, not proof about the student's thinking.

## 5. The four member folders

| Member | Topic folder and instructions |
| --- | --- |
| Bopage | [factorization](../../backend/app/topics/development/factorization/README.md) — Factors of Quadratic Expressions |
| Nimsara | [equations](../../backend/app/topics/development/equations/README.md) — Equations |
| Fernando | [algebraic_fractions](../../backend/app/topics/development/algebraic_fractions/README.md) — Algebraic Fractions |
| Sadeepa | [indices_logs](../../backend/app/topics/development/indices_logs/README.md) — Indices and Logarithms |

Every folder has the same starter source structure, so this explanation applies to all four:

| File | What its functions do |
| --- | --- |
| `generator.py` | `generate_question()` tries AI, validates the returned question, then attempts manual fallback on failure. The topic class delegates its contract methods to these functions and supplies the provider hook. |
| `ai.py` | `configuration()` reads topic-specific environment values. `generate_question()` and `analyze_answer()` are TODOs for the member's chosen provider. `TopicFeedbackProvider.analyze()` plugs analysis into shared verification. |
| `manual.py` | TODOs for deterministic generation, `validate_question()`, feedback and teaching advice. `verify_answer()` validates the question, checks the submitted ID and compares it with the key. |
| `verifier.py` | Its `verify_answer()` calls the manual checker and shared verification service. It does not duplicate AI/fallback logic. This is for independent topic testing; the shared assessment route directly uses the shared service. |
| `__init__.py` | Marks the folder as a package; no provider is called on import. |

These four topics are **unfinished**, not working Mathematics implementations. Their fallback can only generate real questions after the manual TODOs are complete. `development/__init__.py` identifies the shared workspace package; its [README](../../backend/app/topics/development/README.md) is the member index.

## 6. One complete submission flow

1. The frontend sends a test ID, question ID, option ID and access token.
2. `main.py` passes the URL to `assessments.py`; `supabase_auth.py` verifies the user.
3. `submit_test_answer()` checks membership and loads the server's saved question.
4. If an answer already exists, the route returns it. Otherwise `verify_answer()` determines correctness and attempts AI feedback with automatic manual fallback.
5. The route inserts the verified grade, misconception and feedback snapshot into `mathroot_answers`.
6. `review()` builds the response, and the frontend displays it. Later student and teacher requests read the same snapshot.

The unique key `(test_id, question_id, student_id)` prevents duplicates even if requests arrive together. The score is calculated from saved answers, so refreshing the browser does not reset or inflate it.

## 7. Database, tests and supporting files

| Database table | Saved information |
| --- | --- |
| `profiles` | Full name, approved role and requested role. |
| `mathroot_classes` | Class ID, teacher ID and join code. |
| `mathroot_class_members` | Student/class enrollment. |
| `mathroot_tests` | Title, class/teacher IDs and saved questions as JSON. |
| `mathroot_answers` | Submitted option, authenticated student ID, correctness, misconception, timestamp and verification snapshot. |

The existing assessment tables use RLS with no browser grants; the privileged backend client can bypass RLS, so server permission checks are essential. The [verification migration](../../supabase/migrations/20261023143546_answer_verification_feedback.sql) adds a nullable JSONB snapshot column; existing answers remain valid.

| Supporting source | Purpose |
| --- | --- |
| [tests/conftest.py](../../backend/tests/conftest.py) | `Query` imitates the database in memory. The `client` fixture supplies disposable records and a controlled user; automated tests do not need live student records. |
| [tests/test_binomial.py](../../backend/tests/test_binomial.py) | Checks generated mathematics, option consistency, hidden answers and topic readiness. |
| [tests/test_assessments.py](../../backend/tests/test_assessments.py) | Tests enrollment, persistence, resume, scores, duplicate races, roles, ownership and deletion. `seed`, `enroll` and `teacher` prepare test scenarios. |
| [tests/test_answer_verification.py](../../backend/tests/test_answer_verification.py) | Uses `GroundedProvider` and mocked HTTP responses to test AI success, rejection, fallback, snapshots, custom providers and safe symbolic parsing. |
| [tests/test_network_errors.py](../../backend/tests/test_network_errors.py) | Checks HTTP/1.1 configuration and readable 503 responses for network failures. |
| [scripts/verify_assessments.py](../../backend/scripts/verify_assessments.py) | Optional live integration check. `account()` creates disposable users, `ok()` checks responses, and `main()` runs the workflow and cleans up its own records. Unlike unit tests, it needs live services. |
| [requirements.txt](../../backend/requirements.txt) | Declares backend dependencies. The code also imports `supabase` and `python-dotenv`; these are installed in the current environment but are not listed in this file yet. |

## 8. Run and explain it in the viva

From `backend`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```

Backend `.env` contains `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` and the private `SUPABASE_SECRET_KEY`. Question generation uses `MATHROOT_GENERATOR`; answer feedback separately uses `MATHROOT_ANSWER_VERIFIER`. Both support `auto` and `manual`. The default answer-analysis timeout is 4 seconds; a slow model triggers fallback. Each unfinished member topic has its own provider environment prefix.

Remember these distinctions when answering questions:

- **Authentication:** Who is the user? **Authorization:** May this user access this class/test?
- **AI generation:** Proposes question coefficients. **Mathematical validation:** Checks that the question/options are sound.
- **Grading:** Compares the selected ID with the verified key. **AI feedback:** Helps explain supported mistakes.
- **401:** login problem. **403:** insufficient permission. **404:** missing resource. **422:** invalid input. **503:** temporary service failure.
- Current submissions are MCQs. Free-text verification and the four additional topic implementations are not active features.

**Viva answer:** “The backend verifies identity and class membership, grades against the saved answer key, optionally uses validated AI feedback, and stores the result. Rule-based fallback keeps grading available when the AI service fails.”
