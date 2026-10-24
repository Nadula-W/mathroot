# Frontend — what it does and how it connects

**For code-by-code explanations, open the [matching source-file index](SOURCE_INDEX.md).** Each source file now has its own Markdown explanation with actual code blocks. This page remains the overview.

[Back to the viva guide](../README.md) · [Backend guide](../backend/README.md)

The frontend is the part students and teachers see. **Next.js** provides pages and navigation, **React** updates the screen, and **TypeScript** checks the expected data shapes while developing.

## 1. Small code terms you should know

| Code | Simple meaning |
| --- | --- |
| Component | A function that returns part of the screen. |
| `.tsx` | TypeScript containing HTML-like React markup, called JSX. |
| `"use client"` | Enables browser interactions such as buttons and React state. Initial HTML can still be rendered on the server. |
| `useState` | Remembers values such as a selected answer or loading flag. Changing state updates the screen. |
| `useEffect` | Runs work after rendering, such as fetching tests. Its cleanup prevents old requests from changing the current screen. |
| `async` / `await` | Waits for a request without freezing the page. |
| `try` / `catch` / `finally` | Attempts work, handles an error, and clears loading state. |
| `type` | Describes a data shape; it does not validate a server response at runtime. |
| `props` | Values passed from one component to another. |

## 2. Pages and layouts

Paths below are relative to `frontend/`. Click a filename to open its code.

| Source file | What its code does |
| --- | --- |
| [app/layout.tsx](../../frontend/app/layout.tsx) | `RootLayout` wraps every page in HTML/body, loads shared CSS, defines the browser title/description and mounts the language provider and existing selector. `children` means the page inside the layout. |
| [app/globals.css](../../frontend/app/globals.css) | Shared colours, spacing, buttons, panels, question options and account-header styles. Media queries adapt layouts to small screens. |
| [app/page.tsx](../../frontend/app/page.tsx) | `Home` shows the landing page and workspace links using the selected language. |
| [app/register/page.tsx](../../frontend/app/register/page.tsx) | `register()` checks name/password fields, then calls Supabase `signUp`. It sends the name and requested role. Requesting teacher access does not grant an approved teacher role. |
| [app/login/page.tsx](../../frontend/app/login/page.tsx) | `login()` calls `signInWithPassword`, reads the profile, then navigates to student, teacher or pending approval. |
| [app/auth/callback/route.ts](../../frontend/app/auth/callback/route.ts) | A server request handler rather than a visible page. `GET()` exchanges an authentication code for a session and redirects to login. |
| [app/pending-teacher/page.tsx](../../frontend/app/pending-teacher/page.tsx) | Shows the approval-pending message and a `logout()` action. It does not approve accounts. |
| [app/student/layout.tsx](../../frontend/app/student/layout.tsx) | Wraps student pages in `ProtectedArea` with `area="student"`. |
| [app/teacher/layout.tsx](../../frontend/app/teacher/layout.tsx) | Uses the same wrapper with `area="teacher"`. |
| [app/student/page.tsx](../../frontend/app/student/page.tsx) | The student dashboard. The first effect loads joined classes/results; the second loads tests when the selected class changes. `join()` submits the class ID and join code, then reloads membership. |
| [app/student/test/[testId]/page.tsx](../../frontend/app/student/test/%5BtestId%5D/page.tsx) | The test screen. `[testId]` is a URL value read by `useParams`. Loading fetches questions and saved progress. `submit()` sends the option, receives feedback and reloads progress. `advance()` finds the next unanswered question. Completion uses the saved score. |
| [app/teacher/page.tsx](../../frontend/app/teacher/page.tsx) | Arranges `ClassManager`, `TestCreator` and `TestManager` into the teacher dashboard. |

## 3. Shared and teacher components

| Source file | Main functions and connections |
| --- | --- |
| [components/ProtectedArea.tsx](../../frontend/app/components/ProtectedArea.tsx) | Runs on the server. Verifies the Supabase user, reads the profile and redirects accounts to the correct area. It passes the registered name to `AccountHeader`. FastAPI still checks permissions independently. |
| [components/AccountHeader.tsx](../../frontend/app/components/AccountHeader.tsx) | Displays the name, role and navigation. `logout()` signs out, returns to login and refreshes the page. |
| [components/LanguageSelector.tsx](../../frontend/app/components/LanguageSelector.tsx) | Reuses the global English / සිංහල control. It reads and changes the shared language state rather than keeping a separate preference. |
| [components/AssessmentReview.tsx](../../frontend/app/components/AssessmentReview.tsx) | Receives a `SavedResult` prop and displays scores and submitted-answer feedback. Both the student test page and teacher manager reuse it. It does not calculate grades or call AI. |
| [teacher/ClassManager.tsx](../../frontend/app/teacher/ClassManager.tsx) | `reload()` gets the teacher's classes. `createClass()` creates/retrieves a class and shows its join code. It emits `assessments-changed` so sibling components reload. |
| [teacher/TestCreator.tsx](../../frontend/app/teacher/TestCreator.tsx) | Loads classes/topics. `toggle()` selects topics; `createTest()` sends title, class, difficulty and question count. `jsonRequest()` delegates to `backendApi`. Successful creation emits the same refresh event. |
| [teacher/TestManager.tsx](../../frontend/app/teacher/TestManager.tsx) | `reload()` lists tests/classes; `showResults()` loads a summary; `inspect()` loads one student's answers; `copy()` copies a student link; `remove()` confirms deletion, calls the API and reloads. Class filtering happens in the displayed list. |

The component paths in this table are inside `app/`. The refresh event is only a browser notification between components; it is not a database update or realtime subscription.

## 4. API and authentication helpers

| Source file | Purpose |
| --- | --- |
| [lib/backend-api.ts](../../frontend/lib/backend-api.ts) | `backendApi<T>()` reads the session, attaches `Authorization: Bearer <access token>`, calls `/backend` plus the API path, parses JSON and turns failed responses into readable errors. |
| [lib/supabase/client.ts](../../frontend/lib/supabase/client.ts) | Creates the Supabase browser client used by forms, logout and `backendApi`. |
| [lib/supabase/server.ts](../../frontend/lib/supabase/server.ts) | Creates the cookie-aware server client used by `ProtectedArea`. |
| [proxy.ts](../../frontend/proxy.ts) | Refreshes/validates the session for student and teacher URLs and carries updated cookies into the response. The layouts perform the role redirects. |
| [next.config.ts](../../frontend/next.config.ts) | Rewrites `/backend/*` to FastAPI on port 8000. This connects frontend requests to the Python server. |

**Two different paths:** login/registration go directly to Supabase Auth. Assessment requests go through `backendApi` to FastAPI. Protected assessment tables are not queried directly from the browser.

## 5. Follow one button from start to finish

For **Submit Answer**:

1. The test page stores the clicked option ID in `selected` state.
2. `submit()` calls `backendApi` with `question_id` and `option_id`.
3. The helper attaches the access token. The Next.js rewrite forwards the request to FastAPI.
4. FastAPI checks identity/membership, grades the answer, obtains feedback and saves it.
5. The page displays the returned explanation and learning tip, then fetches saved progress.
6. After the last answer, `AssessmentReview` displays the database-derived result. Refreshing restores those saved answers.

For **Generate Test**: `TeacherPage → TestCreator.createTest → backendApi → FastAPI → topic generator → Supabase → response`. The refresh event makes `TestManager` show the new test.

## 6. Supporting files and running

| File | Why it exists |
| --- | --- |
| [package.json](../../frontend/package.json) | Lists libraries and `dev`, `build`, `start`, `typecheck`, `test:i18n` commands. |
| [tests/i18n.test.cjs](../../frontend/tests/i18n.test.cjs) | Six focused Node tests for dictionary/placeholder coverage, literal interface keys, reversible display and missing warnings, error wording, native validation wording and English server rendering. Uses the existing TypeScript compiler in memory; adds no test dependency. |
| [package-lock.json](../../frontend/package-lock.json) | Records resolved dependency versions for repeatable installs. |
| [tsconfig.json](../../frontend/tsconfig.json) | TypeScript settings, including strict checks and the `@/` path alias. |
| [next-env.d.ts](../../frontend/next-env.d.ts) | Generated Next.js type declarations. Normally leave it alone. |
| [start_frontend_windows.bat](../../frontend/start_frontend_windows.bat) | Checks Node, installs dependencies if missing, and starts development mode. |

Frontend configuration uses `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` in `frontend/.env.local`. These public settings identify the project; the backend secret key must never go here.

From `frontend`, run `npm run dev -- -p 3000`. Check types with `npm run typecheck`, language helpers with `npm run test:i18n`, and the production build with `npm run build`. The backend must also be running for assessment requests.

## 7. How English and Sinhala connect

The lightweight files in `lib/i18n/` have separate jobs:

| File | Job |
| --- | --- |
| `en.ts` | English interface wording and the set of translation keys. |
| `si.ts` | Matching Sinhala wording for those keys. No browser-extension or external translation resources are used. |
| `core.ts` | Pure helpers for saved preferences, dictionary interpolation, topic labels, response metadata, missing translations and recognized error messages. |
| `LanguageProvider.tsx` | Shared React language state, `useLanguage()` hook and `TranslationWarning` component. Exposes helpers and the selected `en-LK` / `si-LK` locale. |

The initial server render and first client render both use English. After mounting, the provider reads `mathroot.language` from browser storage and applies a stored Sinhala choice. This avoids reading `window` during server rendering. Changing the selector updates the shared context, saves the preference where storage is available, and updates `<html lang>`. Client navigation retains the provider; refresh restores the choice after mounting.

Pages keep canonical data and form state. Translation happens while rendering, so changing language does not rerun question generation, clear a selected answer, recreate a class or alter saved progress. The backend returns original text plus optional `translations.si` metadata. The display helper chooses Sinhala only when a validated translation is present; a missing translation keeps English and displays a notice. Statuses, topic names, difficulty names and stable misconception codes use the reviewed frontend dictionary. User-written titles, names, class IDs, join codes and mathematical expressions are not machine-rewritten.

Fixed validation messages and recognized API/Auth errors use reviewed wording. An unknown external error remains available in its original form; do not assume every possible provider message has a Sinhala equivalent. Dates use the chosen language's locale after mounting rather than relying on differing server/browser defaults. CSS permits Sinhala Unicode text to wrap in existing responsive layouts.

Login and registration attach `validateInput` / `clearValidation` from the provider to form invalid/input events. The browser still checks required/email/length rules; these helpers replace only the visible validation message and clear it when the user edits. Test creation translates its built-in default title and saves the displayed title; a teacher's custom title is preserved.

**One switch:** `LanguageSelector → LanguageProvider state → dictionary/display helpers → existing components`. No second selector, separate language-specific question key or large internationalization framework is involved.

## 8. Test both languages

Run the current frontend type/build checks, then use disposable student and approved-teacher accounts for browser acceptance:

1. Open the homepage. Switch English → Sinhala → English; verify labels and the document language.
2. Select Sinhala, navigate between login/register/dashboard and refresh. Confirm the preference remains. Clear `mathroot.language` to check the English default.
3. Create a class as teacher; join it as student. Check translated validation and error messages without changing the IDs/codes entered.
4. Generate one Binomial test. Open the same test in both languages, switch after selecting an answer, and confirm the selection, question/option IDs and option order remain unchanged.
5. Submit correct and wrong choices. In backend manual-verification mode, check that Sinhala explanation and corrective guidance work without Ollama. Exercise mocked AI-assisted success through automated tests; verify a live model separately when available.
6. Finish the test. Check saved student results and teacher summaries/reviews in both languages, then reopen an older English test.
7. Check narrow/mobile layout and readable Sinhala. For unsupported legacy prose, confirm English remains visible with the missing-translation notice.

Automated checks cover focused language helpers/switching and backend mathematical invariants. They do not establish that real Supabase accounts, email confirmation or a running Ollama model were exercised in a browser. Report those live acceptance steps separately.

## 9. Verification recorded for bilingual support

- `npm run typecheck`: passed.
- `npm run test:i18n`: all six tests passed.
- `npm run build`: production build passed after the final form/title updates.
- Production Chrome smoke: English → Sinhala → English, preference across refresh/navigation, translated homepage/login/register, Sinhala native required/email validation, document language and exactly one selector passed. A 390px viewport had no horizontal overflow. No runtime or hydration errors were observed.
- Actual student/teacher Supabase login, class/test writes and live Ollama inference were not exercised in this browser smoke. Their route behaviour was covered with the backend's fake database and provider mocks, not real account/service calls.

**Viva answer:** “React state handles screen interaction, while Supabase preserves progress. I use a shared authenticated API helper, and reuse the same review component for both student and teacher results.”
