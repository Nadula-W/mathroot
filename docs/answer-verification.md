# Hybrid answer verification

## Behavior and contracts

The existing endpoint remains `POST /api/tests/{test_id}/answers/submit` with `question_id` and `option_id`. Authentication, class membership, the unique answer key and teacher ownership checks remain unchanged. No student-supplied grade or identity is used.

MCQ correctness comes from the saved correct option ID. Question generators continue independently checking their mathematics with SymPy. Ollama can propose a grade and diagnostic feedback, but cannot change that grade. The provider returns Pydantic-validated JSON containing the proposed grade, misconception, confidence and zero-based selections of approved explanation/correction text. The adapter resolves those selections into the internal Analysis model. This follows Ollama's [structured-output schema workflow](https://docs.ollama.com/capabilities/structured-outputs).

AI feedback is intentionally constrained to topic-approved explanations and corrections: free-form mathematical prose cannot be reliably verified by checking its JSON shape. Grade disagreement, unsupported diagnoses, ungrounded feedback, out-of-range selections, low confidence, invalid JSON, missing model, service errors and timeouts all select deterministic manual feedback automatically. A missing distractor label is treated as unknown evidence, not as a correct answer. Existing Binomial distractor labels remain stable for class aggregation.

The result is saved atomically with the answer as `mathroot_answers.verification`, a JSONB snapshot containing verified correctness, feedback, canonical mathematical explanation, corrective guidance, teaching recommendation, method, confidence and safe diagnostic metadata. The row retains the existing authenticated student ID, test ID, question ID, option ID and database timestamp. No prompt, raw model response, session token or private identity is sent to Ollama or exposed by result endpoints.

Retrying returns the original persisted feedback snapshot, including when two requests race on the primary key. Reviews do not invoke the model again. Older answers with a null/missing snapshot use their existing deterministic feedback; they are not regraded or rewritten. Teacher trends continue using the same persisted misconception field. A single wrong choice is a possible misconception, never proof.

## Migration

`supabase/migrations/20261023143546_answer_verification_feedback.sql` adds one nullable JSONB column and its comment. It was applied to the connected mathroot-ai project and the column was verified. Existing data, RLS, grants, primary keys and cascade deletion are preserved. Run this migration in other environments before starting the updated backend. No backfill is required. A missing column is a deployment error: do not bypass persistence by silently dropping feedback.

## Environment

```dotenv
# Separate from MATHROOT_GENERATOR (question generation)
MATHROOT_ANSWER_VERIFIER=auto
# Optional: defaults to MATHROOT_OLLAMA_MODEL / existing qwen3:4b-instruct
MATHROOT_ANSWER_MODEL=qwen3:4b-instruct
# Per HTTP operation timeout; accepted range 0.1–15, default 4 seconds
MATHROOT_ANSWER_TIMEOUT_SECONDS=4
# Accepted range 0.5–1, default 0.8
MATHROOT_ANSWER_MIN_CONFIDENCE=0.8
```

`MATHROOT_ANSWER_VERIFIER=manual` skips Ollama entirely. Invalid numeric settings use the documented defaults. Ollama uses the existing local endpoint, with thinking disabled and a bounded response budget. Timeouts do not affect correctness; a slow or cold model can cause frequent fallback. No paid services or new dependencies were added. Existing Supabase environment variables remain required.

## User interface

The current question interface displays the accepted conceptual feedback, canonical mathematical explanation and learning tip after submission. The shared AssessmentReview displays persisted feedback, the selected/correct answers, possible misconception, corrective guidance and recommended practice for both student and teacher review. Provider prompts and configuration do not appear in the UI. Correct-answer data remains hidden for unanswered questions.

## Extension and limits

### English and Sinhala presentation

The grading and approved-wording checks described above remain canonical and unchanged. `app.presentation` runs after verification when building a response, adding optional `translations.si` display fields and `translation_warnings`. It does not accept a second answer key, modify saved snapshots or relax `Analysis` validation to admit arbitrary translated feedback. The Binomial presentation module recognizes reviewed explanation/feedback forms, including saved historical forms, and supplies manual Sinhala wording without contacting Ollama.

The language selector changes only presentation. Student feedback, saved reviews and teacher recommendations use the same verified result in either language. Unknown historical/free-form wording is retained in English and marked missing if a reviewed template or validated optional translation is unavailable. Existing marks, misconception codes, question/option IDs and completion dates remain intact.

Optional topic translation providers are independent of the answer-analysis provider. They can assist with additional prose after mathematical-token checks and cache reuse, but they cannot choose correctness or bypass the approved explanation list. See [topic contracts](TOPIC_CONTRACT.md) and the [backend source index](backend/SOURCE_INDEX.md) for the hooks and helpers. No database migration or new dependency is required for bilingual display.

See TOPIC_CONTRACT.md for the optional topic hook, stable misconception definitions and provider adapter interface. The current three Binomial distractors support three error categories. Additional categories have reserved codes and teaching recommendations but require diagnostic question variants before they can be inferred. No unrestricted AI diagnosis is permitted.

The bounded `app.safe_symbolic` helper prepares future free-text adapters without executing Python input. It accepts explicit arithmetic and declared variables only. Domain restrictions and topic-specific rules must be checked by those future adapters. Current routes remain MCQ-only.

## Run and test (PowerShell)

```powershell
# Terminal 1, from backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# Terminal 2, from frontend
npm run dev -- -p 3000
# backend tests (mocked Ollama; no live student records)
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
# frontend checks
npm run typecheck
npm run build
# optional live Auth/database/persisted-feedback check from backend
# Creates and cleans up its own disposable users/classes/tests only.
.\.venv\Scripts\python.exe scripts/verify_assessments.py
```

## Verification recorded

The checks below are the recorded results of the earlier answer-verification feature. They are not evidence of a fresh live Supabase/Ollama run for the bilingual feature. Current bilingual automated checks and manual acceptance instructions are documented in the frontend/backend guides; live success must be reported separately when actually exercised.

For the bilingual implementation, the full backend suite passed 103 tests, the six frontend language tests and TypeScript checks passed, and the production build passed. A production Chrome smoke verified switching/persistence/navigation, translated public/auth pages, native validation wording, document language, one selector and mobile width without observed hydration errors. Live Supabase assessment writes and real Ollama inference were not repeated. These results supplement, rather than repeat, the earlier live checks listed below.

- 47 automated backend tests passed. Coverage includes mocked AI success for correct/incorrect choices, distributive and sign mistakes, incorrect AI grades, low confidence, hallucinated feedback/diagnoses, invalid JSON, absent models, service exceptions, timeouts, manual mode, saved snapshot replay and legacy review. Existing tests cover role/membership authorization, cross-student privacy, duplicate insert races, scores and teacher aggregation/deletion. Safe symbolic parsing has malicious-input and equivalence tests.
- TypeScript and the Next.js production build passed.
- Live Supabase integration passed with the new feedback snapshot column, including persisted feedback equality on retry and all original workflow checks. Disposable records were cleaned up; a follow-up query found zero temporary classes.
- Real local Ollama exceeded the 4-second timeout and a subsequent 15-second check. Both returned the correct deterministic grade and fallback feedback. Successful live AI-assisted inference was not confirmed in this session; successful provider responses were exercised with deterministic HTTP/provider mocks.
- Separate-browser UI acceptance was not automated. The pre-existing Starlette/httpx deprecation warning remains non-failing.

Changed for this feature: `backend/app/answer_verification.py`, `backend/app/safe_symbolic.py`, `backend/app/assessments.py`, `backend/app/topics/development/binomial/manual.py`, `backend/tests/test_answer_verification.py`, `backend/tests/conftest.py`, `backend/scripts/verify_assessments.py`, `frontend/app/student/test/[testId]/page.tsx`, `frontend/app/components/AssessmentReview.tsx`, the additive migration, `docs/TOPIC_CONTRACT.md`, and this document. Earlier working-tree changes were preserved.

Post-migration security advisor review found the existing backend-only tables with RLS and no policies (intentional: browser grants are revoked), plus existing handle_new_user execution-privilege warnings and disabled leaked-password protection. This feature does not modify signup triggers or Auth settings. References: [anonymous function execution](https://supabase.com/docs/guides/database/database-linter?lint=0028_anon_security_definer_function_executable), [authenticated function execution](https://supabase.com/docs/guides/database/database-linter?lint=0029_authenticated_security_definer_function_executable), and [password protection](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection).
