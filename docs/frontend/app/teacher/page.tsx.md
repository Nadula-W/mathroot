# page.tsx — code explained

**Source:** [frontend/app/teacher/page.tsx](../../../../frontend/app/teacher/page.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Combines ClassManager, TestCreator and TestManager. The parent layout provides role checks and the shared account header.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.


**Bilingual update:** This module now renders user-facing wording through the shared language helpers where needed. Language changes affect labels and validated display metadata, while existing forms, requests, selected answers and saved grades retain their canonical values.

## Lines 1–6: Code section

```tsx
"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";

import ClassManager from "./ClassManager";
import TestCreator from "./TestCreator";
import TestManager from "./TestManager";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Marks a client component so browser events and React state can be used. Initial HTML may still be server-rendered.

## Lines 7–7: TeacherPage

```tsx
export default function TeacherPage() {
```

**Explanation:**

- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 8–10: Code section

```tsx
  const { t } = useLanguage();
  return <main className="shell teacher-shell"><section className="section-head"><div className="eyebrow">{t("TEACHER WORKSPACE")}</div><h1>{t("From answers to teaching actions.")}</h1><p>{t("Create Mathematics tests and review your students\u2019 progress.")}</p></section><ClassManager /><TestCreator /><TestManager /></main>;
}
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Connected files

Follow these imports to their matching code explanations:

- [app/teacher/ClassManager.tsx](ClassManager.tsx.md)
- [app/teacher/TestCreator.tsx](TestCreator.tsx.md)
- [app/teacher/TestManager.tsx](TestManager.tsx.md)

## How to explain this file in the viva

“Combines ClassManager, TestCreator and TestManager. The parent layout provides role checks and the shared account header.”
