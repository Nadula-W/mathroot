# page.tsx — code explained

**Source:** [frontend/app/page.tsx](../../../frontend/app/page.tsx) · [All frontend explanations](../SOURCE_INDEX.md)

**What and how:** Home displays the bilingual public landing page and links to protected student/teacher routes. The language hook supplies current interface wording.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.


**Bilingual update:** This module now renders user-facing wording through the shared language helpers where needed. Language changes affect labels and validated display metadata, while existing forms, requests, selected answers and saved grades retain their canonical values.

## Lines 1–4: Code section

```tsx
"use client";
import { useLanguage } from "../lib/i18n/LanguageProvider";
import Link from "next/link";

```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.

## Lines 5–8: Home

```tsx
export default function Home() {
  const { t } = useLanguage();
  return (
    <main className="shell">
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 9–13: Code section

```tsx
      <header className="topbar">
        <Link href="/" className="logo"><span className="logo-icon">∑</span>MathRoot <span>AI</span></Link>
        <span className="topbar-tag">{t("O/L Mathematics \u00b7 Development demo")}</span>
      </header>

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 14–19: Code section

```tsx
      <section className="hero">
        <div className="eyebrow">{t("BECS 32253 \u00b7 Intelligent Systems")}</div>
        <h1>{t("Discover the idea behind")}{" "}<em>{t("the mistake.")}</em></h1>
        <p className="lead">{t("A focused mathematics assessment experience for Sri Lankan O/L students, with teaching recommendations for tuition classes.")}</p>
      </section>

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 20–33: Code section

```tsx
      <section className="choice-grid">
        <Link href="/student" className="choice-card">
          <span className="choice-symbol">01</span>
          <div><h2>{t("Student assessment")}</h2><p>{t("Take your teacher’s Mathematics tests, view explanations and review your progress.")}</p></div>
          <span className="choice-arrow">↗</span>
        </Link>
        <Link href="/teacher" className="choice-card">
          <span className="choice-symbol">02</span>
          <div><h2>{t("Teacher overview")}</h2><p>{t("See submitted answers, error patterns, and topic-specific corrective teaching suggestions.")}</p></div>
          <span className="choice-arrow">↗</span>
        </Link>
      </section>

      <div className="note"><strong>{t("How it works:")}</strong> {t("Questions are checked mathematically. AI-assisted feedback uses manual fallback when AI is unavailable. Use your own student or approved teacher account.")}</div>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 34–37: Code section

```tsx
      <footer className="footer">{t("MathRoot AI \u00b7 University project prototype \u00b7 Built for desktop and mobile")}</footer>
    </main>
  );
}
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## How to explain this file in the viva

“Home displays the bilingual public landing page and links to protected student/teacher routes. The language hook supplies current interface wording.”
