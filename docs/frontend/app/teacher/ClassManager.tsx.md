# ClassManager.tsx — code explained

**Source:** [frontend/app/teacher/ClassManager.tsx](../../../../frontend/app/teacher/ClassManager.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Creates or retrieves owned classes, displays join codes, and refreshes teacher components through the local assessments-changed event.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–3: Code section

```tsx
"use client";
import { useEffect, useState } from "react";
import { backendApi } from "../../lib/backend-api";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Marks a client component so browser events and React state can be used. Initial HTML may still be server-rendered.

## Lines 5–10: ClassManager

```tsx
export default function ClassManager() {
  const [id, setId] = useState("demo3");
  const [joinCode, setJoinCode] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [classes, setClasses] = useState<{ class_id: string; join_code: string }[]>([]);
```

**Explanation:**

- `id` stores the typed class ID. The paired setter updates it and triggers rendering.
- `joinCode` stores the returned teacher join code. The paired setter updates it and triggers rendering.
- `message` stores the success/status text. The paired setter updates it and triggers rendering.
- `busy` stores whether an operation is in progress. The paired setter updates it and triggers rendering.
- `classes` stores the joined/owned class list. The paired setter updates it and triggers rendering.

## Lines 11–14: reload

```tsx
  async function reload() {
    try { setClasses(await backendApi<{ class_id: string; join_code: string }[]>("/api/classes")); }
    catch (e) { setMessage(e instanceof Error ? e.message : "Could not load classes."); }
  }
```

**Explanation:**

- `reload()`: Fetches server-backed lists through backendApi and replaces the displayed state while handling errors/loading.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- Line 12: Reloads the membership list after joining; the browser displays what was actually saved by the backend.
- The API paths in this section connect to FastAPI: `/api/classes`. backendApi attaches the access token before sending them.

## Lines 15–15: Code section

```tsx
  useEffect(() => { void reload(); }, []);
```

**Explanation:**

- Runs after rendering. [] means mount; a dependency such as selected/testId reruns when that value changes.

## Lines 17–31: createClass

```tsx
  async function createClass() {
    setBusy(true); setMessage("");
    try {
      const result = await backendApi<{ class_id: string; join_code: string }>(
        `/api/classes?class_id=${encodeURIComponent(id.trim())}`,
        { method: "POST" },
      );
      setJoinCode(result.join_code);
      await reload();
      window.dispatchEvent(new Event("assessments-changed"));
      setMessage(`Class ${result.class_id} is ready. Share the join code with test students.`);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Class setup failed.");
    } finally { setBusy(false); }
  }
```

**Explanation:**

- `createClass()`: Creates/retrieves the teacher-owned class code, refreshes classes and emits the event used by sibling components.
- A local browser event connects sibling teacher tools: creation dispatches it, listeners reload their lists, and cleanup removes listeners.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- The API paths in this section connect to FastAPI: `/api/classes?class_id=`. backendApi attaches the access token before sending them.

## Lines 33–35: Code section

```tsx
  return <section className="panel">
    <h2>Class setup</h2>
    <p>Create the class before generating a test. Students need a join code.</p>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 36–38: Code section

```tsx
    <label className="field"><span>Class ID</span>
      <input value={id} onChange={e => setId(e.target.value)} maxLength={64}/>
    </label>
```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 39–47: Code section

```tsx
    <button type="button" className="button primary" onClick={createClass} disabled={busy || !id.trim()}>
      {busy ? "Working..." : "Create / Get join code"}
    </button>
    {joinCode && <p><strong>Student join code:</strong> <code>{joinCode}</code></p>}
    {message && <p role="status">{message}</p>}
    <h3>My Classes</h3>
    {classes.length === 0 ? <p>No classes loaded yet.</p> : classes.map(group => <div className="test-entry" key={group.class_id}><strong>{group.class_id}</strong><span>Join code: <code>{group.join_code}</code></span></div>)}
  </section>;
}
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- map creates a visible item for each record/option. key gives React a stable identity when the list updates.
- Line 45: Creates a class card for each membership/owned class. On the student page, View Tests changes selected and therefore reruns the class-test effect.

## Connected files

Follow these imports to their matching code explanations:

- [lib/backend-api.ts](../../lib/backend-api.ts.md)

## How to explain this file in the viva

“Creates or retrieves owned classes, displays join codes, and refreshes teacher components through the local assessments-changed event.”
