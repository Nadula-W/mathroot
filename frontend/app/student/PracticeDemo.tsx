"use client";

import Link from "next/link";
import { useState } from "react";

type Option = { id: string; text: string };
type Question = {
  question_id: string;
  topic_id: string;
  difficulty: string;
  statement: string;
  options: Option[];
  class_id: string;
};
type Answer = {
  correct: boolean;
  selected_option: string;
  correct_answer: string;
  suspected_misconception: string | null;
  diagnosis_status: "none" | "suspected" | "repeated_signal";
  feedback: string;
  recommended_next_difficulty: string;
};
type View = "setup" | "question" | "feedback" | "complete";

const TOTAL_QUESTIONS = 5;

async function postJson<T>(endpoint: string, data: object): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/backend${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      body: JSON.stringify(data),
    });
  } catch {
    throw new Error("Cannot connect to the backend. Check that FastAPI is running on port 8000.");
  }
  if (!response.ok) {
    let detail: string = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      if (typeof data.detail === "string") detail = data.detail;
    } catch { /* response was not JSON */ }
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

function formatMisconception(code: string | null): string {
  const names: Record<string, string> = {
    DISTRIBUTION_CONSTANT: "Multiplying the constant inside brackets",
    DISTRIBUTION_VARIABLE: "Multiplying the variable term inside brackets",
    SIGN_ERROR: "Positive and negative sign operations",
  };
  return code ? names[code] ?? code.replaceAll("_", " ").toLowerCase() : "No misconception indicated";
}

export default function StudentPage() {
  const [classId, setClassId] = useState("demo-class");
  const [studentId, setStudentId] = useState("S001");
  const [activeClass, setActiveClass] = useState("demo-class");
  const [activeStudent, setActiveStudent] = useState("S001");
  const [view, setView] = useState<View>("setup");
  const [question, setQuestion] = useState<Question | null>(null);
  const [selection, setSelection] = useState<string | null>(null);
  const [result, setResult] = useState<Answer | null>(null);
  const [submitted, setSubmitted] = useState(0);
  const [correct, setCorrect] = useState(0);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");

  async function begin() {
    const c = classId.trim();
    const s = studentId.trim();
    if (!c || !s || c.length > 64 || s.length > 64) {
      setError("Enter a class ID and student ID, each up to 64 characters.");
      return;
    }
    setWorking(true); setError("");
    try {
      const next = await postJson<Question>("/api/questions/generate", {
        topic_id: "binomial", difficulty: "easy", class_id: c,
      });
      setActiveClass(c); setActiveStudent(s);
      setQuestion(next); setSelection(null); setResult(null);
      setSubmitted(0); setCorrect(0); setView("question");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not generate a question.");
    } finally { setWorking(false); }
  }

  async function submit() {
    if (!question || !selection) return;
    setWorking(true); setError("");
    try {
      const answer = await postJson<Answer>("/api/answers/submit", {
        question_id: question.question_id,
        option_id: selection,
        student_id: activeStudent,
      });
      setResult(answer);
      setSubmitted((n) => n + 1);
      if (answer.correct) setCorrect((n) => n + 1);
      setView("feedback");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not submit answer.");
    } finally { setWorking(false); }
  }

  async function nextQuestion() {
    if (submitted >= TOTAL_QUESTIONS) { setView("complete"); return; }
    setWorking(true); setError("");
    try {
      const next = await postJson<Question>("/api/practice/next", {
        topic_id: "binomial", class_id: activeClass, student_id: activeStudent,
      });
      setQuestion(next); setSelection(null); setResult(null); setView("question");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load the next question.");
    } finally { setWorking(false); }
  }

  function reset() {
    setView("setup"); setQuestion(null); setSelection(null); setResult(null);
    setError(""); setSubmitted(0); setCorrect(0);
  }

  return (
    <main className="shell student-shell">
      <header className="topbar">
        <Link href="/" className="logo"><span className="logo-icon">∑</span>MathRoot <span>AI</span></Link>
        <Link href="/" className="text-link">← Home</Link>
      </header>

      <section className="section-head">
        <div className="eyebrow">Student workspace</div>
        <h1>Mathematics, one step at a time.</h1>
        <p>Grade 10 · Binomial Expressions · 5-question diagnostic demo</p>
      </section>

      {error && <div className="alert" role="alert">{error}</div>}

      {view === "setup" && (
        <section className="panel narrow">
          <div className="panel-kicker">Before you begin</div>
          <h2>Join a practice session</h2>
          <p className="muted">Use demo IDs only. Your answers will appear in the teacher&apos;s class summary.</p>
          <div className="form-grid">
            <label className="field"><span>Class ID</span><input maxLength={64} value={classId} onChange={(e) => setClassId(e.target.value)} placeholder="demo-class" /></label>
            <label className="field"><span>Student ID</span><input maxLength={64} value={studentId} onChange={(e) => setStudentId(e.target.value)} placeholder="S001" /></label>
          </div>
          <button className="button primary full" disabled={working} onClick={begin}>{working ? "Preparing question…" : "Start assessment →"}</button>
          <p className="helper">No account needed for this local prototype.</p>
        </section>
      )}

      {(view === "question" || view === "feedback") && question && (
        <section className="panel assessment-panel">
          <div className="progress-row"><span className="panel-kicker">Question {submitted + (view === "question" ? 1 : 0)} of {TOTAL_QUESTIONS}</span><span className="difficulty">{question.difficulty} level</span></div>
          <div className="progress"><span style={{ width: `${Math.min(100, ((submitted + (view === "question" ? 1 : 0)) / TOTAL_QUESTIONS) * 100)}%` }} /></div>
          <div className="question-area">
            <span className="question-label">EXPAND AND SIMPLIFY</span>
            <h2>{question.statement}</h2>
            <p className="muted">Choose the expression you believe is correct.</p>
          </div>
          <div className="options" role="radiogroup" aria-label="Answer choices">
            {question.options.map((option, index) => {
              const selected = selection === option.id;
              const correctAfter = !!result && option.text === result.correct_answer;
              return (
                <button key={option.id} type="button" role="radio" aria-checked={selected}
                  className={`option ${selected ? "selected" : ""} ${correctAfter ? "is-correct" : ""}`}
                  disabled={view !== "question" || working} onClick={() => setSelection(option.id)}>
                  <span className="option-index">{String.fromCharCode(65 + index)}</span><span className="option-text">{option.text}</span><span className="option-status">{correctAfter ? "✓" : selected ? "●" : ""}</span>
                </button>
              );
            })}
          </div>
          {view === "question" && <button className="button primary full" disabled={!selection || working} onClick={submit}>{working ? "Checking answer…" : "Submit answer →"}</button>}

          {view === "feedback" && result && (
            <div className={`feedback-box ${result.correct ? "good" : "review"}`} aria-live="polite">
              <div className="feedback-title">{result.correct ? "✓ Correct answer" : "Review this concept"}</div>
              <p>{result.feedback}</p>
              {!result.correct && <><p><strong>Correct answer:</strong> {result.correct_answer}</p><p><strong>Possible difficulty:</strong> {formatMisconception(result.suspected_misconception)}</p><span className="tag">{result.diagnosis_status === "repeated_signal" ? "Repeated error signal" : "Unconfirmed — one answer is not a diagnosis"}</span></>}
              <button className="button primary full" disabled={working} onClick={nextQuestion}>{working ? "Preparing…" : submitted >= TOTAL_QUESTIONS ? "View session result →" : "Next question →"}</button>
            </div>
          )}
        </section>
      )}

      {view === "complete" && (
        <section className="panel narrow finished">
          <span className="finish-icon">✓</span>
          <div className="panel-kicker">Practice completed</div>
          <h2>Well done for completing the assessment.</h2>
          <p className="muted">You answered {correct} of {TOTAL_QUESTIONS} questions correctly. Your teacher can view the class&apos;s answer patterns in the dashboard.</p>
          <button className="button primary full" onClick={reset}>Start another assessment</button>
          <Link className="button ghost full" href="/">Back to home</Link>
        </section>
      )}
      <footer className="footer">Local prototype only · Diagnoses are preliminary, not confirmed learning conditions</footer>
    </main>
  );
}
