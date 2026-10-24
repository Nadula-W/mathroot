# page.tsx — code explained

**Source:** [frontend/app/page.tsx](../../../frontend/app/page.tsx) · [All frontend explanations](../SOURCE_INDEX.md)

**What and how:** Home displays the public landing page and links to protected student/teacher routes. Some milestone text is older than the working assessment features.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–1: Code section

```tsx
import Link from "next/link";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.

## Lines 3–5: Home

```tsx
export default function Home() {
  return (
    <main className="shell">
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 6–9: Code section

```tsx
      <header className="topbar">
        <Link href="/" className="logo"><span className="logo-icon">∑</span>MathRoot <span>AI</span></Link>
        <span className="topbar-tag">O/L Mathematics · Development demo</span>
      </header>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 11–15: Code section

```tsx
      <section className="hero">
        <div className="eyebrow">BECS 32253 · Intelligent Systems</div>
        <h1>Discover the idea behind <em>the mistake.</em></h1>
        <p className="lead">A focused mathematics assessment experience for Sri Lankan O/L students, with teaching recommendations for tuition classes.</p>
      </section>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 17–30: Code section

```tsx
      <section className="choice-grid">
        <Link href="/student" className="choice-card">
          <span className="choice-symbol">01</span>
          <div><h2>Student assessment</h2><p>Answer five generated Binomial Expressions questions. See explanations and get follow-up practice.</p></div>
          <span className="choice-arrow">↗</span>
        </Link>
        <Link href="/teacher" className="choice-card">
          <span className="choice-symbol">02</span>
          <div><h2>Teacher overview</h2><p>See submitted answers, error patterns, and topic-specific corrective teaching suggestions.</p></div>
          <span className="choice-arrow">↗</span>
        </Link>
      </section>

      <div className="note"><strong>Milestone 2:</strong> The backend generates questions using verified rules. LLM generation, secure accounts, and advanced AI diagnosis are planned for later phases. Use test IDs only.</div>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 31–34: Code section

```tsx
      <footer className="footer">MathRoot AI · University project prototype · Built for desktop and mobile</footer>
    </main>
  );
}
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## How to explain this file in the viva

“Home displays the public landing page and links to protected student/teacher routes. Some milestone text is older than the working assessment features.”
