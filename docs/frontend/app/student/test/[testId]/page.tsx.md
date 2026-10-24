# page.tsx — code explained

**Source:** [frontend/app/student/test/[testId]/page.tsx](../../../../../../frontend/app/student/test/%5BtestId%5D/page.tsx) · [All frontend explanations](../../../../SOURCE_INDEX.md)

**What and how:** The assigned test screen reads testId from the URL, loads safe questions and saved progress together, submits one option, and restores the next unanswered question. AssessmentReview shows the completed saved result.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.


**Bilingual update:** This module now renders user-facing wording through the shared language helpers where needed. Language changes affect labels and validated display metadata, while existing forms, requests, selected answers and saved grades retain their canonical values.

## Lines 1–12: Code section

```tsx
"use client";
import { TranslationWarning, useLanguage } from "../../../../lib/i18n/LanguageProvider";
import type { Translatable } from "../../../../lib/i18n/core";



import { backendApi } from "../../../../lib/backend-api";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import AssessmentReview, { SavedResult } from "../../../components/AssessmentReview";

```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Marks a client component so browser events and React state can be used. Initial HTML may still be server-rendered.

## Lines 13–23: Question

```tsx
type Question = Translatable & {
  question_id: string;
  topic_id: string;
  difficulty: string;
  statement: string;
  options: (Translatable & {
    id: string;
    text: string;
  })[];
};

```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 24–32: Test

```tsx
type Test = {
  test_id: string;
  title: string;
  class_id: string;
  question_count: number;
  topics: string[];
  questions: Question[];
};

```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 33–44: Answer

```tsx
type Answer = Translatable & {
  correct: boolean;
  feedback: string;
  correct_answer: string;
  selected_option: string;
  suspected_misconception: string | null;
  diagnosis_status: string;
  recommended_next_difficulty: string;
  explanation?: string;
  corrective_guidance?: string;
};

```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 45–62: AssignedTestPage

```tsx
export default function AssignedTestPage() {
  const { t, topic, content, errorText } = useLanguage();
  const { testId } = useParams<{ testId: string }>();

  const [test, setTest] = useState<Test | null>(null);
  const [loading, setLoading] = useState(true);
  const [started, setStarted] = useState(false);

  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState("");
  const [feedback, setFeedback] = useState<Answer | null>(null);

  const [saved, setSaved] = useState<SavedResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  // Load the assigned test using the student's
  // authenticated Supabase session.
```

**Explanation:**

- `test` stores the loaded assigned test. The paired setter updates it and triggers rendering.
- `loading` stores the initial-load/form waiting flag. The paired setter updates it and triggers rendering.
- `started` stores whether test interaction has started. The paired setter updates it and triggers rendering.
- `index` stores the zero-based current question position. The paired setter updates it and triggers rendering.
- `selected` stores the selected answer option ID. The paired setter updates it and triggers rendering.
- `feedback` stores the submitted-answer feedback. The paired setter updates it and triggers rendering.
- `saved` stores the saved server result used for scores/resume. The paired setter updates it and triggers rendering.
- `busy` stores whether an operation is in progress. The paired setter updates it and triggers rendering.
- `error` stores the visible error message. The paired setter updates it and triggers rendering.

## Lines 63–71: Code section

```tsx
  useEffect(() => {
    if (!testId) {
      setLoading(false);
      setError("Invalid test link.");
      return;
    }

    let active = true;

```

**Explanation:**

- Runs after rendering. [] means mount; a dependency such as selected/testId reruns when that value changes.

## Lines 72–97: loadTest

```tsx
    async function loadTest() {
      setLoading(true);
      setError("");
      setTest(null);
      setSaved(null);
      setStarted(false);
      setIndex(0);
      setSelected("");
      setFeedback(null);

      try {
        const [data, progress] = await Promise.all([
          backendApi<Test>(`/api/tests/${encodeURIComponent(testId)}`),
          backendApi<SavedResult>(`/api/tests/${encodeURIComponent(testId)}/progress`),
        ]);

        if (!active) return;

        setTest(data);
        setSaved(progress);
        const next = data.questions.findIndex(q => !progress.answers.some(a => a.question_id === q.question_id));
        setIndex(next < 0 ? data.questions.length : next);
        setStarted(progress.answers.length > 0);
      } catch (err) {
        if (!active) return;

```

**Explanation:**

- `loadTest()`: Resets previous test state, loads safe questions plus saved progress and resumes at the first unanswered question.
- Starts independent requests together and returns their results in the order supplied.
- Searches for the first unanswered question using saved answers. -1 means none remain, so the index is moved past the last question.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- Uses the unanswered question position; when findIndex returned -1, sets the position to the question count to show completion.
- Previously saved answers skip a fresh-start introduction so the user can resume.
- The API paths in this section connect to FastAPI: `/api/tests/`. backendApi attaches the access token before sending them.

## Lines 98–118: Code section

```tsx
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load this test."
        );
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadTest();

    return () => {
      active = false;
    };
  }, [testId]);

  // Submit an answer to the Supabase-backed
  // FastAPI endpoint.
```

**Explanation:**

- Cleanup switches off active so late responses cannot update a page after navigation or an older class selection.

## Lines 119–144: submit

```tsx
  async function submit() {
    if (!test || !selected || busy || feedback) {
      return;
    }

    const question = test.questions[index];

    if (!question) return;

    setBusy(true);
    setError("");

    try {
      const answer = await backendApi<Answer>(
        `/api/tests/${encodeURIComponent(
          test.test_id
        )}/answers/submit`,
        {
          method: "POST",
          body: JSON.stringify({
            question_id: question.question_id,
            option_id: selected,
          }),
        }
      );

```

**Explanation:**

- `submit()`: Guards missing/repeated actions, posts question/option IDs, reloads saved progress and shows backend feedback. It does not send a student ID or decide the grade.
- Turns the request object into JSON text for the HTTP body.
- Rejects a submit attempt when data/selection is absent, a request is pending or this question already has displayed feedback.
- The API paths in this section connect to FastAPI: `/api/tests/`. backendApi attaches the access token before sending them.

## Lines 145–161: Code section

```tsx
      // Student ID is NOT sent.
      // FastAPI identifies the student using
      // their verified Supabase access token.

      setSaved(await backendApi<SavedResult>(`/api/tests/${encodeURIComponent(test.test_id)}/progress`));
      setFeedback(answer);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Answer submission failed."
      );
    } finally {
      setBusy(false);
    }
  }

```

**Explanation:**

- Reloads saved progress after submission; scores and resume position come from persisted answers, not a local counter.
- The API paths in this section connect to FastAPI: `/api/tests/`. backendApi attaches the access token before sending them.

## Lines 162–182: advance

```tsx
  function advance() {
    if (!feedback || !test) return;

    const next = test.questions.findIndex(q => !saved?.answers.some(a => a.question_id === q.question_id));
    setIndex(next < 0 ? test.questions.length : next);
    setSelected("");
    setFeedback(null);
    setError("");
  }

  const complete =
    !!test && index >= test.questions.length;

  const question =
    test && !complete
      ? test.questions[index]
      : null;

  return (
    <main className="shell student-shell">

```

**Explanation:**

- `advance()`: Finds the next question missing from saved answers, then clears local option/feedback. It never increments a local score.
- Searches for the first unanswered question using saved answers. -1 means none remain, so the index is moved past the last question.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- Uses the unanswered question position; when findIndex returned -1, sets the position to the question count to show completion.
- Converts test existence to a boolean and checks whether the position is past the final question.

## Lines 183–207: Code section

```tsx
      <section className="section-head">
        <div className="eyebrow">{t("ASSIGNED MATHEMATICS TEST")}</div>

        <h1>
          {loading
            ? t("Loading test...")
            : test?.title || t("Unable to load test")}
        </h1>

        {test && (
          <p>
            {t("Class:")} {test.class_id}
            {" · "}
            {t("{count} questions", { count: test.question_count })}
          </p>
        )}
      </section>

      {/* Display API errors */}
      {error && (
        <div className="alert" role="alert">
          {errorText(error)}
        </div>
      )}

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 208–209: Code section

```tsx
      {/* Loading state */}
      {loading && (
```

**Explanation:**

- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 210–216: Code section

```tsx
        <section className="panel narrow">
          <p>{t("Loading your assigned Mathematics test...")}</p>
        </section>
      )}

      {/* Failed to load the test */}
      {!loading && !test && (
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 217–230: Code section

```tsx
        <section className="panel narrow">
          <p>
            {t("Make sure you are logged in and have joined your teacher's class.")}
          </p>

          <Link
            href="/student"
            className="button primary full"
          >{t("Back to My Tests")}</Link>
        </section>
      )}

      {/* Test introduction */}
      {!loading && !started && test && (
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 231–252: Code section

```tsx
        <section className="panel narrow">
          <h2>{t("Ready to Start?")}</h2>

          <p>{t("You are about to begin:")}</p>

          <h3>{test.title}</h3>

          <p>{t("Class:")}<strong>{test.class_id}</strong>
          </p>

          <p>
            {t("Total Questions:")}{" "}
            <strong>{test.question_count}</strong>
          </p>

          <p>
            {t("Topics:")}{" "}
            <strong>
              {test.topics?.map(topic).join(", ") || t("Mathematics")}
            </strong>
          </p>

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 253–256: Code section

```tsx
          <p className="helper">
            {t("Your answers will be saved automatically under your logged-in student account.")}
          </p>

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 257–274: Code section

```tsx
          <button
            type="button"
            className="button primary full"
            disabled={test.questions.length === 0}
            onClick={() => {
              setStarted(true);
              setError("");
            }}
          >{t("Start Test")}</button>

          <p className="helper">
            {t("Each answer can be submitted only once. Refreshing resumes from your saved answers.")}
          </p>
        </section>
      )}

      {/* Mathematics question */}
      {started && question && (
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 275–293: Code section

```tsx
        <section className="panel assessment-panel">
          <div className="progress-row">
            <strong>
              {t("Question {number} of {total}", { number: index + 1, total: test?.question_count ?? 0 })}
            </strong>

            <span className="difficulty">
              {topic(question.topic_id)}
              {" · "}
              {t(question.difficulty === "easy" ? "Easy" : question.difficulty === "medium" ? "Medium" : "Hard")}
            </span>
          </div>

          <div className="question-area">
            <h2>{content(question, "statement")}</h2>
            <TranslationWarning record={question} fields={["statement"]} />
          </div>

          {/* Answer options */}
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 294–295: Code section

```tsx
          <div className="options">
            {question.options.map((option, i) => (
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- map creates a visible item for each record/option. key gives React a stable identity when the list updates.

## Lines 296–320: Code section

```tsx
              <button
                key={option.id}
                type="button"
                className={`option ${
                  selected === option.id
                    ? "selected"
                    : ""
                }`}
                disabled={!!feedback || busy}
                onClick={() => setSelected(option.id)}
              >
                <span className="option-index">
                  {String.fromCharCode(65 + i)}
                </span>

                <span className="option-text">
                  {content(option, "text")}
                  <TranslationWarning record={option} fields={["text"]} />
                </span>
              </button>
            ))}
          </div>

          {/* Submit answer */}
          {!feedback ? (
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 321–332: Code section

```tsx
            <button
              type="button"
              className="button primary full"
              disabled={!selected || busy}
              onClick={submit}
            >
              {t(busy
                ? "Saving Answer..."
                : "Submit Answer")}
            </button>
          ) : (
            /* AI / Rule-based feedback */
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 333–359: Code section

```tsx
            <div className="feedback-box review">
              <strong>
                {t(feedback.correct
                  ? "Correct!"
                  : "Review your answer")}
              </strong>

              <p>{content(feedback, "feedback")}</p>
              {feedback.explanation && !content(feedback, "feedback").includes(content(feedback, "explanation")) && <p>{content(feedback, "explanation")}</p>}
              {feedback.corrective_guidance && <p>{t("Learning tip:")} {content(feedback, "corrective_guidance")}</p>}
              <TranslationWarning record={feedback} />

              {!feedback.correct && (
                <p>
                  {t("Correct answer:")}{" "}
                  {content(feedback, "correct_answer")}
                </p>
              )}

              {!feedback.correct &&
                feedback.suspected_misconception && (
                  <p className="helper">
                    {t("Possible misconception:")}{" "}
                    {t(feedback.suspected_misconception)}
                  </p>
                )}

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 360–375: Code section

```tsx
              <button
                type="button"
                className="button primary full"
                onClick={advance}
              >
                {t(index + 1 === test?.question_count
                  ? "Finish Test"
                  : "Next Question")}
              </button>
            </div>
          )}
        </section>
      )}

      {/* Completed assessment */}
      {started && complete && test && (
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 376–386: Code section

```tsx
        <section className="panel narrow finished">
          <h2>{t("Test Completed!")}</h2>

          <p>
            {t("You answered {correct} of {total} questions correctly.", { correct: saved?.correct ?? 0, total: test.question_count })}
          </p>

          <p>
            {t("Your answers have been saved. Your teacher can view your results from the teacher dashboard.")}
          </p>

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 387–396: Code section

```tsx
          <Link
            href="/student"
            className="button primary full"
          >{t("Back to My Tests")}</Link>
        </section>
      )}
      {started && complete && saved && <AssessmentReview result={saved} />}
    </main>
  );
}
```

**Explanation:**

- Passes saved result data to the shared renderer instead of regrading it in this page.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Connected files

Follow these imports to their matching code explanations:

- [app/components/AssessmentReview.tsx](../../../components/AssessmentReview.tsx.md)
- [lib/backend-api.ts](../../../../lib/backend-api.ts.md)

## How to explain this file in the viva

“The assigned test screen reads testId from the URL, loads safe questions and saved progress together, submits one option, and restores the next unanswered question. AssessmentReview shows the completed saved result.”
