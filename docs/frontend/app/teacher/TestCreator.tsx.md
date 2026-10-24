# TestCreator.tsx — code explained

**Source:** [frontend/app/teacher/TestCreator.tsx](../../../../frontend/app/teacher/TestCreator.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Loads ready topics and owned classes, collects generation settings and posts them to FastAPI. Mathematics is generated on the backend, not in this form.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.


**Bilingual update:** This module now renders user-facing wording through the shared language helpers where needed. Language changes affect labels and validated display metadata, while existing forms, requests, selected answers and saved grades retain their canonical values.

**Default title:** The built-in practice-test title is displayed in the selected language, and `createTest` submits that displayed default. A teacher's custom title remains their own text. Switching language does not change selected topics, class, difficulty or question count, and only pressing Create sends a generation request.

## Lines 1–7: Code section

```tsx
"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";


import { backendApi } from "../../lib/backend-api";
import { useEffect, useState } from "react";

```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Marks a client component so browser events and React state can be used. Initial HTML may still be server-rendered.

## Lines 8–14: Topic

```tsx
type Topic = {
  id: string;
  name: string;
  owner: string;
  ready: boolean;
};

```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 15–22: TestInfo

```tsx
type TestInfo = {
  test_id: string;
  title: string;
  class_id: string;
  question_count: number;
  topics: string[];
};

```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 23–34: jsonRequest

```tsx
async function jsonRequest<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const path = url.startsWith("/backend/")
    ? url.slice("/backend".length)
    : url;

  return backendApi<T>(path, options);
}


```

**Explanation:**

- `jsonRequest()`: Normalizes legacy /backend prefixes and delegates the actual authenticated request to backendApi.

## Lines 35–47: TestCreator

```tsx
export default function TestCreator() {
  const { t, topic: topicLabel, errorText } = useLanguage();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selected, setSelected] = useState<string[]>(["binomial"]);
  const [classId, setClassId] = useState("");
  const [title, setTitle] = useState("O/L Mathematics Practice Test");
  const [count, setCount] = useState(3);
  const [difficulty, setDifficulty] = useState("easy");
  const [classes, setClasses] = useState<{ class_id: string }[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

```

**Explanation:**

- `topics` stores the backend topic list. The paired setter updates it and triggers rendering.
- `selected` stores the selected topic ID list. The paired setter updates it and triggers rendering.
- `classId` stores the selected teacher-owned class. The paired setter updates it and triggers rendering.
- `title` stores the test-title input. The paired setter updates it and triggers rendering.
- `count` stores questions per topic. The paired setter updates it and triggers rendering.
- `difficulty` stores the selected difficulty. The paired setter updates it and triggers rendering.
- `classes` stores the joined/owned class list. The paired setter updates it and triggers rendering.
- `busy` stores whether an operation is in progress. The paired setter updates it and triggers rendering.
- `message` stores the success/status text. The paired setter updates it and triggers rendering.
- `error` stores the visible error message. The paired setter updates it and triggers rendering.

## Lines 48–55: Code section

```tsx
  useEffect(() => {
    jsonRequest<Topic[]>("/backend/api/topics")
      .then(setTopics)
      .catch(() =>
        setError("Cannot load topics. Check backend port 8000.")
      );
  }, []);

```

**Explanation:**

- Runs after rendering. [] means mount; a dependency such as selected/testId reruns when that value changes.
- then receives successful request data, catch records an error, and finally clears loading even after failure.

## Lines 56–61: Code section

```tsx
  useEffect(() => {
    const load = () => { backendApi<{ class_id: string }[]>("/api/classes").then(setClasses).catch(e => setError(e.message)); };
    load(); window.addEventListener("assessments-changed", load);
    return () => window.removeEventListener("assessments-changed", load);
  }, []);

```

**Explanation:**

- Runs after rendering. [] means mount; a dependency such as selected/testId reruns when that value changes.
- A local browser event connects sibling teacher tools: creation dispatches it, listeners reload their lists, and cleanup removes listeners.
- The API paths in this section connect to FastAPI: `/api/classes`. backendApi attaches the access token before sending them.
- then receives successful request data, catch records an error, and finally clears loading even after failure.

## Lines 62–69: toggle

```tsx
  function toggle(topicId: string) {
    setSelected((previous) =>
      previous.includes(topicId)
        ? previous.filter((id) => id !== topicId)
        : [...previous, topicId]
    );
  }

```

**Explanation:**

- `toggle()`: Adds/removes a topic ID without changing other selected topics.
- filter creates the displayed subset, such as tests in the chosen class, without changing the original list.

## Lines 70–95: createTest

```tsx
  async function createTest() {
    if (!classId.trim() || !title.trim() || selected.length === 0) {
      setError("Enter class ID, title and select a topic.");
      return;
    }

    setBusy(true);
    setError("");
    setMessage("");

    try {
      const created = await jsonRequest<TestInfo>(
        "/backend/api/tests",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: (title === "O/L Mathematics Practice Test" ? t(title) : title).trim(),
            class_id: classId.trim(),
            topic_ids: selected,
            questions_per_topic: count,
            difficulty,
          }),
        }
      );

```

**Explanation:**

- `createTest()`: Sends the selected class/title/topics/count/difficulty to FastAPI and triggers a test-list reload after success.
- Turns the request object into JSON text for the HTTP body.

## Lines 96–105: Code section

```tsx
      setMessage(`Test created: ${created.title}`);
      window.dispatchEvent(new Event("assessments-changed"));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Creation failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
```

**Explanation:**

- A local browser event connects sibling teacher tools: creation dispatches it, listeners reload their lists, and cleanup removes listeners.

## Lines 106–113: Code section

```tsx
    <section className="panel" style={{ marginBottom: 24 }}>
      <div className="panel-kicker">{t("Teacher Assessment Builder")}</div>
      <h2>{t("Create Mathematics Test")}</h2>

      {error && <div className="alert">{errorText(error)}</div>}
      {message && <div className="alert soft">{errorText(message)}</div>}

      <div className="form-grid">
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- Renders an error message only when error contains text; an empty value produces no error panel.

## Lines 114–118: Code section

```tsx
        <label className="field">
          <span>{t("Class ID")}</span>
          <select value={classId} onChange={e => setClassId(e.target.value)}><option value="">{t("Select your class")}</option>{classes.map(c => <option key={c.class_id}>{c.class_id}</option>)}</select>
        </label>

```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- map creates a visible item for each record/option. key gives React a stable identity when the list updates.

## Lines 119–132: Code section

```tsx
        <label className="field">
          <span>{t("Test Title")}</span>
          <input
            value={title === "O/L Mathematics Practice Test" ? t(title) : title}
            maxLength={100}
            onChange={(e) => setTitle(e.target.value)}
          />
        </label>
      </div>

      <h3>{t("Select Mathematics Topics")}</h3>

      <div className="topic-choices">
        {topics.map((topic) => (
```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- map creates a visible item for each record/option. key gives React a stable identity when the list updates.

## Lines 133–151: Code section

```tsx
          <label className="topic-choice" key={topic.id}>
            <input
              type="checkbox"
              checked={selected.includes(topic.id)}
              disabled={!topic.ready || busy}
              onChange={() => toggle(topic.id)}
            />
            <span>
              {topicLabel(topic.id)}
              <small>
                {" "}({topic.owner}) —{" "}
                {t(topic.ready ? "Ready" : "Coming soon")}
              </small>
            </span>
          </label>
        ))}
      </div>

      <div className="form-grid">
```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 152–162: Code section

```tsx
        <label className="field">
          <span>{t("Questions per Topic")}</span>
          <input
            type="number"
            min={1}
            max={10}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
          />
        </label>

```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 163–175: Code section

```tsx
        <label className="field">
          <span>{t("Difficulty")}</span>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
          >
            <option value="easy">{t("Easy")}</option>
            <option value="medium">{t("Medium")}</option>
            <option value="hard">{t("Hard")}</option>
          </select>
        </label>
      </div>

```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 176–192: Code section

```tsx
      <button
        className="button primary"
        onClick={createTest}
        disabled={
          busy || !classId ||
          selected.length === 0 ||
          !Number.isInteger(count) ||
          count < 1 ||
          count > 10
        }
      >
        {t(busy ? "Working..." : "Generate Test")}
      </button>

    </section>
  );
}
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Connected files

Follow these imports to their matching code explanations:

- [lib/backend-api.ts](../../lib/backend-api.ts.md)

## How to explain this file in the viva

“Loads ready topics and owned classes, collects generation settings and posts them to FastAPI. Mathematics is generated on the backend, not in this form.”
