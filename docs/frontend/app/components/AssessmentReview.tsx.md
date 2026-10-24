# AssessmentReview.tsx — code explained

**Source:** [frontend/app/components/AssessmentReview.tsx](../../../../frontend/app/components/AssessmentReview.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Receives SavedResult from student or teacher pages and displays stored grades, answers, explanations and tips. It neither grades nor calls AI.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.


**Bilingual update:** Uses the shared language hook for labels, topic/status names, timestamps and validated response text. Saved answers keep canonical values, while TranslationWarning marks fields without safe Sinhala wording. It neither regrades nor calls a model.

## Lines 1–12: SavedAnswer

```tsx
"use client";

import { TranslationWarning, useLanguage } from "../../lib/i18n/LanguageProvider";
import type { Translatable } from "../../lib/i18n/core";

export type SavedAnswer = Translatable & {
  question_id: string; statement: string; option_id: string; correct: boolean;
  selected_option: string; correct_answer: string; explanation: string;
  feedback: string; suspected_misconception: string | null;
  corrective_guidance?: string; teaching_recommendation?: string;
  verification_method?: "ai_assisted" | "manual_fallback";
};
```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 13–17: SavedResult

```tsx
export type SavedResult = {
  title: string; topics: string[]; status: string; question_count: number;
  correct: number; incorrect: number; percentage: number; completed_at: string | null;
  answers: SavedAnswer[];
};
```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 18–18: AssessmentReview

```tsx
export default function AssessmentReview({ result }: { result: SavedResult }) {
```

**Explanation:**

- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 19–34: Code section

```tsx
  const { t, topic, content, locale } = useLanguage();
  return <section className="panel">
    <h2>{result.title} — {t(result.status)}</h2><p>{result.topics.map(topic).join(", ")}</p>
    <p>{result.correct}/{result.question_count} ({result.percentage}%) · {t("{correct} correct · {incorrect} incorrect", { correct: result.correct, incorrect: result.incorrect })}</p>
    {result.completed_at && <p>{t("Completed {date}", { date: new Date(result.completed_at).toLocaleString(locale) })}</p>}
    {result.answers.map(answer => <article className="feedback-box review" key={answer.question_id}>
      <h3>{content(answer, "statement")}</h3><p>{t(answer.correct ? "Correct" : "Incorrect")} · {t("Your answer:")} {content(answer, "selected_option")}</p>
      <p>{t("Correct answer:")} {content(answer, "correct_answer")}</p><p>{content(answer, "explanation")}</p><p>{content(answer, "feedback")}</p>
      {answer.suspected_misconception && <p>{t("Possible misconception:")} {t(answer.suspected_misconception)}</p>}
      {answer.corrective_guidance && <p>{t("Learning tip:")} {content(answer, "corrective_guidance")}</p>}
      {answer.teaching_recommendation && <p>{t("Recommended practice:")} {content(answer, "teaching_recommendation")}</p>}
      <TranslationWarning record={answer} />
    </article>)}
    <p className="helper">{t("Wrong answers suggest possible misconceptions; they do not prove them.")}</p>
  </section>;
}
```

**Explanation:**

- Formats a returned timestamp for the viewer without changing its stored completion time.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- map creates a visible item for each record/option. key gives React a stable identity when the list updates.
- Builds one saved-answer review card per submitted question, showing the selected/correct text and persisted feedback.

## How to explain this file in the viva

“Receives SavedResult from student or teacher pages and displays stored grades, answers, explanations and tips. It neither grades nor calls AI.”
