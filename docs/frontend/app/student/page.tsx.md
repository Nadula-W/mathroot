# page.tsx — code explained

**Source:** [frontend/app/student/page.tsx](../../../../frontend/app/student/page.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** The student dashboard loads joined classes/results, loads tests when a class is selected, and posts class ID/code to join. Saved results come from FastAPI, not browser-only scores.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–4: Code section

```tsx
"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { backendApi } from "../../lib/backend-api";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Marks a client component so browser events and React state can be used. Initial HTML may still be server-rendered.

## Lines 5–5: Group

```tsx
type Group = { class_id: string; teacher_name: string | null };
```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 6–6: Test

```tsx
type Test = { test_id: string; title: string; topics: string[]; difficulty: string; question_count: number; status: string; correct: number; incorrect: number; percentage: number; completed_at: string | null };
```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 7–11: StudentPage

```tsx
export default function StudentPage() {
  const [classes, setClasses] = useState<Group[]>([]), [tests, setTests] = useState<Test[]>([]), [results, setResults] = useState<Test[]>([]);
  const [selected, setSelected] = useState(""), [id, setId] = useState(""), [code, setCode] = useState("");
  const [loading, setLoading] = useState(true), [joining, setJoining] = useState(false), [testsLoading, setTestsLoading] = useState(false);
  const [error, setError] = useState(""), [message, setMessage] = useState("");
```

**Explanation:**

- `classes` stores this student's joined classes. The paired setter updates it and triggers rendering.
- `tests` stores the available or teacher-owned test list. The paired setter updates it and triggers rendering.
- `results` stores this student's completed saved tests. The paired setter updates it and triggers rendering.
- `selected` stores the selected class ID, whose change reloads class tests. The paired setter updates it and triggers rendering.
- `id` stores the typed class ID. The paired setter updates it and triggers rendering.
- `code` stores the typed student join code. The paired setter updates it and triggers rendering.
- `loading` stores the initial-load/form waiting flag. The paired setter updates it and triggers rendering.
- `joining` stores whether joining is in progress. The paired setter updates it and triggers rendering.
- `testsLoading` stores whether class tests are loading. The paired setter updates it and triggers rendering.
- `error` stores the visible error message. The paired setter updates it and triggers rendering.
- `message` stores the success/status text. The paired setter updates it and triggers rendering.

## Lines 12–18: Code section

```tsx
  useEffect(() => {
    let active = true;
    Promise.all([backendApi<Group[]>("/api/student/classes"), backendApi<Test[]>("/api/student/results")])
      .then(([groups, saved]) => { if (active) { setClasses(groups); setResults(saved); setSelected(groups[0]?.class_id || ""); } })
      .catch(e => { if (active) setError(e.message); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
```

**Explanation:**

- Runs after rendering. [] means mount; a dependency such as selected/testId reruns when that value changes.
- Cleanup switches off active so late responses cannot update a page after navigation or an older class selection.
- Starts independent requests together and returns their results in the order supplied.
- Line 15: Selects the first joined class automatically; ?. handles an empty class list, and || supplies an empty selection.
- The API paths in this section connect to FastAPI: `/api/student/classes`, `/api/student/results`. backendApi attaches the access token before sending them.
- then receives successful request data, catch records an error, and finally clears loading even after failure.

## Lines 19–28: Code section

```tsx
  useEffect(() => {
    let active = true;
    setTests([]);
    if (!selected) return;
    setTestsLoading(true);
    backendApi<Test[]>(`/api/tests?class_id=${encodeURIComponent(selected)}`)
      .then(data => { if (active) setTests(data); }).catch(e => { if (active) setError(e.message); })
      .finally(() => { if (active) setTestsLoading(false); });
    return () => { active = false; };
  }, [selected]);
```

**Explanation:**

- Runs after rendering. [] means mount; a dependency such as selected/testId reruns when that value changes.
- Cleanup switches off active so late responses cannot update a page after navigation or an older class selection.
- Line 21: Clears the previous class's tests so they are not displayed under the newly selected class.
- Line 22: Stops before requesting tests when no class is selected.
- Line 24: Safely inserts the selected class ID into the query string; special characters cannot accidentally change the URL parameters.
- The API paths in this section connect to FastAPI: `/api/tests?class_id=`. backendApi attaches the access token before sending them.
- then receives successful request data, catch records an error, and finally clears loading even after failure.

## Lines 29–36: join

```tsx
  async function join() {
    setJoining(true); setError(""); setMessage("");
    try {
      const data = await backendApi<{ status: string }>("/api/classes/join", { method: "POST", body: JSON.stringify({ class_id: id.trim(), join_code: code.trim() }) });
      setClasses(await backendApi<Group[]>("/api/student/classes")); setSelected(id.trim()); setCode("");
      setMessage(data.status === "already_enrolled" ? "You are already enrolled in this class." : "Class joined successfully.");
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to join class."); } finally { setJoining(false); }
  }
```

**Explanation:**

- `join()`: Posts class ID/code, refreshes persistent memberships, selects the joined class and shows success/already-enrolled status.
- Turns the request object into JSON text for the HTTP body.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- Line 33: Reloads the membership list after joining; the browser displays what was actually saved by the backend.
- Line 33: Clears the join-code input after success so it is not unnecessarily retained in the form.
- Line 34: Chooses a different success message when membership already existed; it is not a new duplicate enrollment.
- The API paths in this section connect to FastAPI: `/api/classes/join`, `/api/student/classes`. backendApi attaches the access token before sending them.

## Lines 37–37: Code section

```tsx
  return <main className="shell student-shell">
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 38–39: Code section

```tsx
    <section className="section-head"><div className="eyebrow">STUDENT WORKSPACE</div><h1>My Mathematics Tests</h1><p>Your classes, assessments and saved feedback.</p></section>
    {error && <p className="alert" role="alert">{error}</p>}{message && <p className="alert soft" role="status">{message}</p>}
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- Line 39: Renders an error message only when error contains text; an empty value produces no error panel.

## Lines 40–40: Code section

```tsx
    <section className="panel"><h2>Join a Class</h2><div className="form-grid">
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 41–41: Code section

```tsx
      <label className="field"><span>Class ID</span><input value={id} maxLength={64} onChange={e => setId(e.target.value)} /></label>
```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 42–42: Code section

```tsx
      <label className="field"><span>Teacher join code</span><input value={code} maxLength={128} onChange={e => setCode(e.target.value)} /></label></div>
```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 43–43: Code section

```tsx
      <button className="button primary" disabled={joining || !id.trim() || !code.trim()} onClick={join}>{joining ? "Joining..." : "Join Class"}</button></section>
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 44–44: Code section

```tsx
    <section className="panel"><h2>My Classes</h2>{loading ? <p role="status">Loading classes...</p> : classes.length === 0 ? <p>Join your teacher’s class using its ID and code.</p> : classes.map(group => <div className="test-entry" key={group.class_id}><div><strong>{group.class_id}</strong><p>{group.teacher_name || "Teacher"}</p></div><button className="button" aria-pressed={selected === group.class_id} onClick={() => { setError(""); setSelected(group.class_id); }}>View Tests</button></div>)}</section>
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- map creates a visible item for each record/option. key gives React a stable identity when the list updates.
- Line 44: Creates a class card for each membership/owned class. On the student page, View Tests changes selected and therefore reruns the class-test effect.

## Lines 45–45: Code section

```tsx
    <section className="panel"><h2>Available Tests {selected && `— ${selected}`}</h2>{testsLoading ? <p role="status">Loading tests...</p> : !selected ? <p>Select a joined class.</p> : tests.length === 0 ? <p>No tests assigned yet.</p> : tests.map(test => <div className="test-entry" key={test.test_id}><div><h3>{test.title}</h3><p>{test.topics.join(", ")} · {test.difficulty} · {test.question_count} questions · {test.status}</p></div><Link className="button primary" href={`/student/test/${test.test_id}`}>{test.status === "Completed" ? "View Results" : test.status === "In Progress" ? "Continue Test" : "Start Test"}</Link></div>)}</section>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- map creates a visible item for each record/option. key gives React a stable identity when the list updates.
- Line 45: Creates one test card per server result, using the saved test ID as the React key and navigation target.
- Line 45: The saved status determines the button label: View Results, Continue Test or Start Test. All labels lead to the same resumable test URL.

## Lines 46–48: Code section

```tsx
    <section className="panel"><h2>My Results</h2>{loading ? <p>Loading results...</p> : results.length === 0 ? <p>Completed tests will appear here.</p> : results.map(test => <div className="test-entry" key={test.test_id}><div><h3>{test.title}</h3><p>{test.correct}/{test.question_count} ({test.percentage}%) · {test.correct} correct · {test.incorrect} incorrect</p><p>{test.completed_at && new Date(test.completed_at).toLocaleString()}</p></div><Link className="button" href={`/student/test/${test.test_id}`}>View detailed feedback</Link></div>)}</section>
  </main>;
}
```

**Explanation:**

- Formats a returned timestamp for the viewer without changing its stored completion time.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- map creates a visible item for each record/option. key gives React a stable identity when the list updates.
- Line 46: Creates the My Results cards from previously completed server results, including score/counts and a detailed-review link.

## Connected files

Follow these imports to their matching code explanations:

- [lib/backend-api.ts](../../lib/backend-api.ts.md)

## How to explain this file in the viva

“The student dashboard loads joined classes/results, loads tests when a class is selected, and posts class ID/code to join. Saved results come from FastAPI, not browser-only scores.”
