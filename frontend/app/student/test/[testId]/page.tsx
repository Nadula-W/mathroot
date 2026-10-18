
"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

type Question = {
  question_id: string;
  topic_id: string;
  difficulty: string;
  statement: string;
  options: { id: string; text: string }[];
};

type Test = {
  test_id: string;
  title: string;
  class_id: string;
  question_count: number;
  questions: Question[];
};

type Answer = {
  correct: boolean;
  feedback: string;
  correct_answer: string;
};

export default function AssignedTestPage() {
  const { testId } = useParams<{ testId: string }>();

  const [test, setTest] = useState<Test | null>(null);
  const [studentId, setStudentId] = useState("");
  const [started, setStarted] = useState(false);
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState("");
  const [feedback, setFeedback] = useState<Answer | null>(null);
  const [correct, setCorrect] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!testId) return;

    fetch(
      `/backend/api/tests/${encodeURIComponent(testId)}`,
      { cache: "no-store" }
    )
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("Test not found. Check the shared link.");
        }

        return (await response.json()) as Test;
      })
      .then(setTest)
      .catch((e: Error) => setError(e.message));
  }, [testId]);

  async function submit() {
    if (!test || !selected || busy) return;

    setBusy(true);
    setError("");

    try {
      const response = await fetch(
        "/backend/api/answers/submit",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question_id: test.questions[index].question_id,
            option_id: selected,
            student_id: studentId.trim(),
          }),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail || "Answer could not be submitted."
        );
      }

      const answer = result as Answer;
      setFeedback(answer);

      if (answer.correct) {
        setCorrect((n) => n + 1);
      }
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Submission failed."
      );
    } finally {
      setBusy(false);
    }
  }

  function advance() {
    setIndex((i) => i + 1);
    setSelected("");
    setFeedback(null);
    setError("");
  }

  const complete = !!test && index >= test.questions.length;
  const question = !complete && test
    ? test.questions[index]
    : null;

  return (
    <main className="shell student-shell">
      <header className="topbar">
        <Link href="/" className="logo">
          MathRoot AI
        </Link>
      </header>

      <section className="section-head">
        <div className="eyebrow">Assigned Mathematics Test</div>
        <h1>{test?.title || "Loading test..."}</h1>
        {test && (
          <p>
            Class: {test.class_id}
            {" · "}
            {test.question_count} questions
          </p>
        )}
      </section>

      {error && (
        <div className="alert" role="alert">{error}</div>
      )}

      {!started && test && (
        <section className="panel narrow">
          <label className="field">
            <span>Student ID (Demo)</span>
            <input
              maxLength={64}
              value={studentId}
              onChange={(e) =>
                setStudentId(e.target.value)
              }
            />
          </label>

          <button
            className="button primary full"
            disabled={!studentId.trim()}
            onClick={() => setStarted(true)}
          >
            Start Test
          </button>

          <p className="helper">
            This version does not support resuming a test
            after refreshing the page.
          </p>
        </section>
      )}

      {started && question && (
        <section className="panel assessment-panel">
          <div className="progress-row">
            <strong>
              Question {index + 1} of {test?.question_count}
            </strong>
            <span className="difficulty">
              {question.topic_id} · {question.difficulty}
            </span>
          </div>

          <div className="question-area">
            <h2>{question.statement}</h2>
          </div>

          <div className="options">
            {question.options.map((option, i) => (
              <button
                key={option.id}
                type="button"
                className={`option ${
                  selected === option.id ? "selected" : ""
                }`}
                disabled={!!feedback || busy}
                onClick={() => setSelected(option.id)}
              >
                <span className="option-index">
                  {String.fromCharCode(65 + i)}
                </span>

                <span className="option-text">
                  {option.text}
                </span>
              </button>
            ))}
          </div>

          {!feedback ? (
            <button
              className="button primary full"
              disabled={!selected || busy}
              onClick={submit}
            >
              {busy ? "Submitting..." : "Submit Answer"}
            </button>
          ) : (
            <div className="feedback-box review">
              <strong>
                {feedback.correct
                  ? "Correct!"
                  : "Review your answer"}
              </strong>

              <p>{feedback.feedback}</p>

              {!feedback.correct && (
                <p>
                  Correct answer: {feedback.correct_answer}
                </p>
              )}

              <button
                className="button primary full"
                onClick={advance}
              >
                {index + 1 === test?.question_count
                  ? "Finish Test"
                  : "Next Question"}
              </button>
            </div>
          )}
        </section>
      )}

      {started && complete && (
        <section className="panel narrow finished">
          <h2>Test Completed!</h2>

          <p>
            You answered {correct} of{" "}
            {test?.question_count} questions correctly.
          </p>

          <p>
            Your teacher can see your results in the dashboard.
          </p>

          <Link href="/" className="button ghost full">
            Home
          </Link>
        </section>
      )}
    </main>
  );
}
