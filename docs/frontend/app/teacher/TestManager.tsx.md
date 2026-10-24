# TestManager.tsx — code explained

**Source:** [frontend/app/teacher/TestManager.tsx](../../../../frontend/app/teacher/TestManager.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Lists and filters owned tests, copies student links, opens summaries/student reviews and confirms deletion. AssessmentReview renders detailed saved answers.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.


**Bilingual update:** This module now renders user-facing wording through the shared language helpers where needed. Language changes affect labels and validated display metadata, while existing forms, requests, selected answers and saved grades retain their canonical values.

## Lines 1–7: Code section

```tsx
"use client";
import { TranslationWarning, useLanguage } from "../../lib/i18n/LanguageProvider";
import type { Translatable } from "../../lib/i18n/core";

import { useEffect, useState } from "react";
import { backendApi } from "../../lib/backend-api";
import AssessmentReview, { SavedResult } from "../components/AssessmentReview";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Marks a client component so browser events and React state can be used. Initial HTML may still be server-rendered.

## Lines 8–8: Test

```tsx
type Test = { test_id: string; title: string; class_id: string; topics: string[]; difficulty: string; question_count: number; created_at: string | null; participant_count: number };
```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 9–9: Results

```tsx
type Results = { title: string; enrolled_count: number; student_count: number; completed_count: number; average_score: number | null; highest_score: number | null; lowest_score: number | null; students: { student_id: string; full_name: string; status: string; correct: number; incorrect: number; percentage: number }[]; topics_results: { topic_id: string; misconceptions: (Translatable & { code: string; count: number; recommendation: string })[] }[] };
```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 10–14: TestManager

```tsx
export default function TestManager() {
  const { t, topic: topicLabel, content, errorText, locale } = useLanguage();
  const [tests, setTests] = useState<Test[]>([]), [classes, setClasses] = useState<{ class_id: string }[]>([]);
  const [filter, setFilter] = useState(""), [error, setError] = useState(""), [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false), [results, setResults] = useState<Results | null>(null), [review, setReview] = useState<SavedResult | null>(null), [testId, setTestId] = useState("");
```

**Explanation:**

- `tests` stores the available or teacher-owned test list. The paired setter updates it and triggers rendering.
- `classes` stores the joined/owned class list. The paired setter updates it and triggers rendering.
- `filter` stores the class filter on the teacher list. The paired setter updates it and triggers rendering.
- `error` stores the visible error message. The paired setter updates it and triggers rendering.
- `message` stores the success/status text. The paired setter updates it and triggers rendering.
- `busy` stores whether an operation is in progress. The paired setter updates it and triggers rendering.
- `results` stores saved student results or the selected teacher summary. The paired setter updates it and triggers rendering.
- `review` stores the selected student's detailed result. The paired setter updates it and triggers rendering.
- `testId` stores the selected test ID. The paired setter updates it and triggers rendering.

## Lines 15–19: reload

```tsx
  async function reload() {
    setBusy(true); setError("");
    try { const [data, groups] = await Promise.all([backendApi<Test[]>("/api/teacher/tests"), backendApi<{ class_id: string }[]>("/api/classes")]); setTests(data); setClasses(groups); }
    catch (e) { setError(e instanceof Error ? e.message : "Unable to load tests."); } finally { setBusy(false); }
  }
```

**Explanation:**

- `reload()`: Fetches server-backed lists through backendApi and replaces the displayed state while handling errors/loading.
- Starts independent requests together and returns their results in the order supplied.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- The API paths in this section connect to FastAPI: `/api/teacher/tests`, `/api/classes`. backendApi attaches the access token before sending them.

## Lines 20–20: Code section

```tsx
  useEffect(() => { void reload(); const refresh = () => { void reload(); }; window.addEventListener("assessments-changed", refresh); return () => window.removeEventListener("assessments-changed", refresh); }, []);
```

**Explanation:**

- Runs after rendering. [] means mount; a dependency such as selected/testId reruns when that value changes.
- A local browser event connects sibling teacher tools: creation dispatches it, listeners reload their lists, and cleanup removes listeners.

## Lines 21–24: showResults

```tsx
  async function showResults(id: string) {
    setBusy(true); setError(""); setResults(null); setReview(null); setTestId(id);
    try { setResults(await backendApi<Results>(`/api/tests/${id}/results`)); } catch (e) { setError(e instanceof Error ? e.message : "Unable to load results."); } finally { setBusy(false); }
  }
```

**Explanation:**

- `showResults()`: Clears stale detail, remembers the test ID and fetches its owned-teacher result summary.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- The API paths in this section connect to FastAPI: `/api/tests/`. backendApi attaches the access token before sending them.

## Lines 25–30: remove

```tsx
  async function remove(test: Test) {
    if (!window.confirm(t("Delete “{title}”? This permanently deletes this test and all its student submissions and results.", { title: test.title }))) return;
    setBusy(true); setError("");
    try { await backendApi(`/api/tests/${test.test_id}`, { method: "DELETE" }); if (testId === test.test_id) { setResults(null); setReview(null); } setMessage("Test and its submissions deleted."); await reload(); }
    catch (e) { setError(e instanceof Error ? e.message : "Deletion failed."); } finally { setBusy(false); }
  }
```

**Explanation:**

- `remove()`: Confirms the destructive action, deletes through the API and refreshes the list. Database cascade removes the related answers.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- Requires the user to confirm deletion before any DELETE request is sent.
- The API paths in this section connect to FastAPI: `/api/tests/`. backendApi attaches the access token before sending them.

## Lines 31–34: inspect

```tsx
  async function inspect(studentId: string) {
    setBusy(true); setError(""); setReview(null);
    try { setReview(await backendApi<SavedResult>(`/api/tests/${testId}/students/${studentId}`)); } catch (e) { setError(e instanceof Error ? e.message : "Unable to load answers."); } finally { setBusy(false); }
  }
```

**Explanation:**

- `inspect()`: Fetches one student's detailed answers for the selected test. FastAPI checks teacher ownership.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- The API paths in this section connect to FastAPI: `/api/tests/`. backendApi attaches the access token before sending them.

## Lines 35–37: copy

```tsx
  async function copy(id: string) {
    try { await navigator.clipboard.writeText(`${window.location.origin}/student/test/${id}`); setMessage("Student link copied. Students must join the class before opening it."); } catch { setError("Clipboard unavailable. Open the student link and copy its address."); }
  }
```

**Explanation:**

- `copy()`: Writes the student URL to the clipboard and reports success/failure. Membership is still needed to use the link.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- Copies the full current-origin student link; clipboard errors are caught for a readable message.

## Lines 38–38: Code section

```tsx
  return <section className="panel"><h2>{t("Manage Mathematics Tests")}</h2>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 39–39: Code section

```tsx
    <label className="field"><span>{t("Filter by class")}</span><select value={filter} onChange={e => setFilter(e.target.value)}><option value="">{t("All my classes")}</option>{classes.map(c => <option key={c.class_id}>{c.class_id}</option>)}</select></label>
```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- map creates a visible item for each record/option. key gives React a stable identity when the list updates.

## Lines 40–50: Code section

```tsx
    <button className="button" disabled={busy} onClick={reload}>{t("Reload Tests")}</button>
    {busy && <p role="status">{t("Loading...")}</p>}{error && <p className="alert" role="alert">{errorText(error)}</p>}{message && <p role="status">{errorText(message)}</p>}
    {!busy && tests.filter(t => !filter || t.class_id === filter).length === 0 && <p>{t("No tests in this selection. Create a class and generate a test above.")}</p>}
    {tests.filter(t => !filter || t.class_id === filter).map(test => <article className="test-entry" key={test.test_id}><div><h3>{test.title}</h3><p>{t("Class:")} {test.class_id} · {test.topics.map(topicLabel).join(", ")} · {t(test.difficulty === "easy" ? "Easy" : test.difficulty === "medium" ? "Medium" : "Hard")}</p><p>{t("{count} questions", { count: test.question_count })} · {t("{count} participating students", { count: test.participant_count })} · {test.created_at && new Date(test.created_at).toLocaleString(locale)}</p></div><div className="test-buttons"><button className="button" disabled={busy} onClick={() => showResults(test.test_id)}>{t("View Results")}</button><button className="button" onClick={() => copy(test.test_id)}>{t("Copy Student Link")}</button><a href={`/student/test/${test.test_id}`} className="text-link">{t("Student Link")}</a><button className="button" disabled={busy} onClick={() => remove(test)}>{t("Delete Test")}</button></div></article>)}
    {results && <div><h3>{t("Results \u2014 {title}", { title: results.title })}</h3><p>{t("{enrolled} enrolled \u00b7 {attempted} attempted \u00b7 {completed} completed", { enrolled: results.enrolled_count, attempted: results.student_count, completed: results.completed_count })}</p><p>{t("Completed scores: average {average}% \u00b7 highest {highest}% \u00b7 lowest {lowest}%", { average: results.average_score ?? "-", highest: results.highest_score ?? "-", lowest: results.lowest_score ?? "-" })}</p>
      {results.students.length === 0 && <p>{t("No submissions yet.")}</p>}
      {results.students.map(s => <article className="test-entry" key={s.student_id}><div><strong>{s.full_name === "Student" ? t("Student") : s.full_name}</strong><p>{t(s.status)} · {t("{correct} correct \u00b7 {incorrect} incorrect", { correct: s.correct, incorrect: s.incorrect })} · {s.percentage}%</p></div><button className="button" disabled={busy} onClick={() => inspect(s.student_id)}>{t("Inspect answers")}</button></article>)}
      <h3>{t("Common misconceptions and teaching actions")}</h3>{results.topics_results.map(topic => <div key={topic.topic_id}><h4>{topicLabel(topic.topic_id)}</h4>{topic.misconceptions.length === 0 && <p>{t("No misconception signals recorded.")}</p>}{topic.misconceptions.map(m => <p key={m.code}>{t(m.code)}: {t("{count} signals.", { count: m.count })} {content(m, "recommendation")}<TranslationWarning record={m} fields={["recommendation"]} /></p>)}</div>)}
    </div>}{review && <AssessmentReview result={review} />}
  </section>;
}
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- Formats a returned timestamp for the viewer without changing its stored completion time.
- Passes saved result data to the shared renderer instead of regrading it in this page.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- map creates a visible item for each record/option. key gives React a stable identity when the list updates.
- filter creates the displayed subset, such as tests in the chosen class, without changing the original list.
- Renders an error message only when error contains text; an empty value produces no error panel.

## Connected files

Follow these imports to their matching code explanations:

- [app/components/AssessmentReview.tsx](../components/AssessmentReview.tsx.md)
- [lib/backend-api.ts](../../lib/backend-api.ts.md)

## How to explain this file in the viva

“Lists and filters owned tests, copies student links, opens summaries/student reviews and confirms deletion. AssessmentReview renders detailed saved answers.”
