"use client";

import Link from "next/link";
import { useState } from "react";
import TestCreator from "./TestCreator";

type MisconceptionCount = { code: string; answer_count: number };
type Recommendation = { code: string; action: string };
type Summary = {
  class_id: string;
  topic_id: string;
  total_answers: number;
  students: number;
  correct_answers: number;
  misconception_counts: MisconceptionCount[];
  recommendations: Recommendation[];
  note: string;
};

const nameFor: Record<string, string> = {
  DISTRIBUTION_CONSTANT: "Incomplete multiplication of the constant",
  DISTRIBUTION_VARIABLE: "Incomplete multiplication of the variable",
  SIGN_ERROR: "Sign errors during expansion",
};

export default function TeacherPage() {
  const [classId, setClassId] = useState("demo-class");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function refresh() {
    const id = classId.trim();
    if (!id || id.length > 64) { setError("Enter a class ID (up to 64 characters)."); return; }
    setError(""); setLoading(true);
    try {
      const url = `/backend/api/teacher/summary?class_id=${encodeURIComponent(id)}&topic_id=binomial`;
      const response = await fetch(url, { cache: "no-store" });
      if (!response.ok) throw new Error(`Unable to load class summary (${response.status}).`);
      setSummary((await response.json()) as Summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot connect to FastAPI on port 8000.");
      setSummary(null);
    } finally { setLoading(false); }
  }

  const accuracy = summary && summary.total_answers > 0
    ? Math.round((summary.correct_answers / summary.total_answers) * 100)
    : 0;

  return (
    <main className="shell teacher-shell">
      <header className="topbar">
        <Link href="/" className="logo"><span className="logo-icon">∑</span>MathRoot <span>AI</span></Link>
        <Link href="/" className="text-link">← Home</Link>
      </header>
      <section className="section-head">
        <div className="eyebrow">Teacher workspace · Demo</div>
        <h1>From answers to teaching actions.</h1>
        <p>Grade 10 · Binomial Expressions · Class-level response analysis</p>
      </section>
      <div className="alert soft" role="note">This page has no login or privacy controls yet. Use test IDs only; do not enter real children&apos;s names or personal records.</div>
      <TestCreator />
      <section className="panel control-panel">
        <div><div className="panel-kicker">Select your class</div><h2>Class feedback</h2></div>
        <div className="class-controls">
          <label className="field"><span>Class ID</span><input maxLength={64} value={classId} onChange={(e) => setClassId(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") void refresh(); }} /></label>
          <button className="button primary" disabled={loading} onClick={refresh}>{loading ? "Loading…" : "Load feedback →"}</button>
        </div>
      </section>
      {error && <div className="alert" role="alert">{error}</div>}
      {!summary && !error && <div className="empty-state"><span>◎</span><h2>No feedback loaded yet</h2><p>Enter the same class ID used in a student assessment and press Load feedback.</p></div>}
      {summary && <>
        <section className="stats-grid">
          <div className="stat"><span>Students who answered</span><strong>{summary.students}</strong><small>Unique student IDs</small></div>
          <div className="stat"><span>Answers submitted</span><strong>{summary.total_answers}</strong><small>Across all questions</small></div>
          <div className="stat"><span>Correct answers</span><strong>{summary.correct_answers}</strong><small>{accuracy}% of answers</small></div>
        </section>
        <div className="teacher-grid">
          <section className="panel">
            <div className="panel-kicker">Response patterns</div>
            <h2>Common error signals</h2>
            <p className="muted">Counts represent incorrect answers, not confirmed misconceptions or unique students.</p>
            {summary.misconception_counts.length === 0 ? (
              <p className="empty-inline">No incorrect response patterns recorded for this class yet.</p>
            ) : (
              <div className="misconceptions">
                {summary.misconception_counts.map((item) => (
                  <div className="misconception" key={item.code}>
                    <div className="misconception-row"><span>{nameFor[item.code] ?? item.code}</span><strong>{item.answer_count}</strong></div>
                    <div className="bar-track"><div style={{ width: `${Math.min(100, (item.answer_count / Math.max(1, summary.total_answers)) * 100)}%` }} /></div>
                  </div>
                ))}
              </div>
            )}
          </section>
          <section className="panel">
            <div className="panel-kicker">Teacher suggestions</div>
            <h2>Recommended next steps</h2>
            <p className="muted">Suggestions are based on observed error options and should be reviewed by the teacher.</p>
            {summary.recommendations.length === 0 ? (
              <p className="empty-inline">Teaching suggestions appear after incorrect student answers are recorded.</p>
            ) : (
              <div className="recommendations">
                {summary.recommendations.map((item, i) => (
                  <div className="recommendation" key={item.code}><span className="rec-no">{String(i + 1).padStart(2, "0")}</span><p>{item.action}</p></div>
                ))}
              </div>
            )}
          </section>
        </div>
        <p className="helper">{summary.note}</p>
      </>}
      <footer className="footer">Teacher dashboard MVP · Next phases: teacher authentication, student-level review and generated worksheets</footer>
    </main>
  );
}
