# Assessment workflow implementation

The student workspace now discovers persistent memberships through `/api/student/classes`, selects a joined class, and loads its tests with the verified session. Joining requires both the class ID and join code. The existing account header obtains the registered full name from `profiles`.

## Root causes

- `/student` had no membership discovery API or initial load. It required typing a class ID on every visit, with a default different from the test creator. The API correctly rejected unenrolled users, but the UI did not restore enrolled classes.
- Direct test links supplied the missing test ID; they did not fix class discovery. Both entry points now check the same server-side membership.
- The teacher summary used plain fetch without a bearer token. Teacher management now uses `backendApi` throughout.
- The assigned test page kept its question index and score only in React state. Refreshing lost progress and attempted to submit already saved answers. The API now returns saved progress, calculates scores from persisted answers, and returns the original answer on retries, including a database unique-key race.
- There were no student saved-results or teacher all-tests/delete APIs. Those routes are implemented and used by the dashboards.
- Each page rendered a brand header in addition to the shared account header. The duplicate headers and inaccurate no-auth warning were removed.

## Main files

- `backend/app/assessments.py`: membership discovery, progress and result summaries, submitted-answer-only review, teacher management, ownership checks, transactional cascade deletion, pagination, generation through the configured topic for every question.
- `backend/app/supabase_auth.py`: profile/database failures return 503 rather than being reported as an invalid session.
- `frontend/app/student/page.tsx`: My Classes, Available Tests, My Results and join controls.
- `frontend/app/student/test/[testId]/page.tsx`: authenticated load, saved progress restoration, server-derived scores and detailed result view; keeps the existing question interface.
- `frontend/app/components/AssessmentReview.tsx`: shared submitted-answer feedback display for student and teacher.
- `frontend/app/teacher/page.tsx`, `ClassManager.tsx`, `TestCreator.tsx`, `TestManager.tsx`: owned class selection and join codes, generation, refreshable test management, filter, results, individual review, copy and confirmed delete.
- `frontend/lib/backend-api.ts`: bearer-token requests and readable validation errors.
- `backend/tests`: isolated assessment API tests and retained Binomial/SymPy generation invariants. Old endpoint tests were updated because the working tree's existing Supabase-only entry point had already removed SQLite practice endpoints.
- `backend/scripts/verify_assessments.py`: opt-in live API integration check with unique disposable accounts and class records; cleans up its own records.

The initial working tree already contained changes to `main.py`, student pages, teacher pages, TestCreator and the new backend-api helper. This work builds on those changes; it does not replace the application entry point or mathematics topic contracts.

## Database and migrations

No SQL migration is required for the connected `mathroot-ai` project. Read-only inspection verified the actual columns of `profiles`, `mathroot_classes`, `mathroot_class_members`, `mathroot_tests` and `mathroot_answers`.

The existing `mathroot_answers` primary key is `(test_id, question_id, student_id)`. Its `test_id` foreign key already has `ON DELETE CASCADE`. A single authorized test DELETE therefore removes associated answers atomically while retaining the class and unrelated tests. No extra attempts table is needed: each submitted answer is immutable, an attempt starts with its first answer, completion means all saved question IDs have answers, and completion time is the last saved answer timestamp. Starting without submitting an answer remains Not Started.

RLS is enabled on all five tables. The browser roles have no table grants for the four assessment tables; protected operations go through FastAPI with its backend-only privileged client. `authenticated` can SELECT profiles under the existing own-profile policy. Full question JSON with hidden answers must remain unavailable through direct browser database access. This matches Supabase's [RLS and grants guidance](https://supabase.com/docs/guides/database/postgres/row-level-security).

For another Supabase project, compare these schema and security requirements before using this implementation. This is not a bootstrap migration for a blank project.

## Environment

Backend `backend/.env`:

```dotenv
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLIC_KEY
SUPABASE_SECRET_KEY=YOUR_BACKEND_ONLY_SECRET
# Optional; current defaults are shown:
MATHROOT_GENERATOR=auto
MATHROOT_OLLAMA_MODEL=qwen3:4b-instruct
```

Frontend `frontend/.env.local`:

```dotenv
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLIC_KEY
```

No new environment variables are required. Keep the backend secret out of NEXT_PUBLIC variables. The existing Next.js rewrite sends `/backend/*` to port 8000. Ollama is expected at `http://127.0.0.1:11434`; generation retains the existing rule-based fallback and SymPy verification.

## Run and verify

From `backend`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

From `frontend`, in another terminal:

```powershell
npm run dev -- -p 3000
```

Automated checks:

```powershell
# backend
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
# frontend
npm run typecheck
npm run build
```

Optional live API check (creates and deletes ONLY its own disposable accounts, classes, tests and submissions):

```powershell
# backend, with Supabase credentials configured and network access
.\.venv\Scripts\python.exe scripts/verify_assessments.py
```

Use separate browser profiles for the final UI acceptance check: an approved teacher creates a class and three-question test; a student joins with its code, selects the class, answers one question, refreshes, completes it, and revisits My Results; the teacher inspects the named student's feedback and deletes a disposable test after confirmation. Use a new class ID if `demo3` already exists; do not change its existing records for testing.

Class averages/highest/lowest include completed attempts only; the dashboard labels this explicitly. Individual partial scores use the full test question count, and incorrect counts include answered questions only. Misconception feedback remains preliminary evidence, not a confirmed diagnosis.

## API additions

| Method | Path | Access |
| --- | --- | --- |
| GET | `/api/student/classes` | Student's memberships, no join codes |
| GET | `/api/student/results` | Student's completed tests in joined classes |
| GET | `/api/tests/{test_id}/progress` | Enrolled student, own submitted answers only |
| GET | `/api/teacher/tests` | Approved teacher's tests |
| GET | `/api/tests/{test_id}/students/{student_id}` | Owning teacher's submitted-answer review |
| DELETE | `/api/tests/{test_id}` | Owning approved teacher; cascades only this test's answers |

Existing create, join, list, test detail, submission, test results and class summary routes remain available. Student identity comes exclusively from the verified Supabase token. Correct answers and explanations appear only for submitted questions in student responses.

## Verification recorded during implementation

- Backend automated checks: 11 passed, covering role and membership enforcement, pending teachers, missing tokens, forged student IDs, submitted-answer-only review, progress restoration, duplicate retries and an insert race, correct scoring, cross-student isolation, teacher ownership, generation persistence and cascade deletion. The generator invariant test checks 300 generated questions with SymPy.
- Frontend TypeScript check and production build passed. Build worker spawning required running outside the restricted sandbox.
- Live API integration passed against the connected Supabase project with verified password sessions and unique disposable teacher/student accounts. It exercised generation, joining, discovery, persisted answers, retries, student results, named teacher results, cross-class/student/teacher access rejection, and deletion while retaining a second disposable test. Cleanup removed the created accounts, class, membership and test records. A read-only follow-up found zero `codex-check-*` classes.
- Ollama status during that run: auto mode, qwen3:4b-instruct installed and available. The existing generator can fall back per question; the status endpoint does not certify the origin of every saved question.
- Separate-browser-profile UI acceptance and visual mobile review were not automated in this session. The live integration uses FastAPI TestClient with real Supabase Auth/database requests, rather than a browser driving Next.js.
- A pre-existing Starlette/httpx deprecation warning remains in the test environment; it does not fail tests.

## Windows connection troubleshooting

The backend Supabase clients explicitly use pooled HTTP/1.1 connections. This avoids the observed concurrent HTTP/2 read failure (`httpx.ReadError`, WinError 10035). Transport failures return a readable 503; an authentication-service network failure no longer reports an invalid login. Writes are not automatically replayed. Restart FastAPI after changing the client configuration. Verification: 14 backend tests passed and 12 concurrent read-only Supabase requests passed with six workers.

Hydration diffs containing extra `bis_skin_checked`, `bis_register` or `__processed_*` attributes indicate browser-injected markup. Check in an extension-free browser profile, or disable the injecting extension for localhost, then reload. The application does not generate these attributes. Do not add broad hydration-warning suppression to conceal them. See [Next.js hydration guidance](https://nextjs.org/docs/messages/react-hydration-error).
