
"use client";

import { backendApi } from "../../../../lib/backend-api";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import AssessmentReview, { SavedResult } from "../../../components/AssessmentReview";

type Question = {
  question_id: string;
  topic_id: string;
  difficulty: string;
  statement: string;
  options: {
    id: string;
    text: string;
  }[];
};

type Test = {
  test_id: string;
  title: string;
  class_id: string;
  question_count: number;
  topics: string[];
  questions: Question[];
};

type Answer = {
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

export default function AssignedTestPage() {
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
  useEffect(() => {
    if (!testId) {
      setLoading(false);
      setError("Invalid test link.");
      return;
    }

    let active = true;

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

      <section className="section-head">
        <div className="eyebrow">
          ASSIGNED MATHEMATICS TEST
        </div>

        <h1>
          {loading
            ? "Loading test..."
            : test?.title || "Unable to load test"}
        </h1>

        {test && (
          <p>
            Class: {test.class_id}
            {" · "}
            {test.question_count} questions
          </p>
        )}
      </section>

      {/* Display API errors */}
      {error && (
        <div className="alert" role="alert">
          {error}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <section className="panel narrow">
          <p>Loading your assigned Mathematics test...</p>
        </section>
      )}

      {/* Failed to load the test */}
      {!loading && !test && (
        <section className="panel narrow">
          <p>
            Make sure you are logged in and have joined
            your teacher's class.
          </p>

          <Link
            href="/student"
            className="button primary full"
          >
            Back to My Tests
          </Link>
        </section>
      )}

      {/* Test introduction */}
      {!loading && !started && test && (
        <section className="panel narrow">
          <h2>Ready to Start?</h2>

          <p>
            You are about to begin:
          </p>

          <h3>{test.title}</h3>

          <p>
            Class: <strong>{test.class_id}</strong>
          </p>

          <p>
            Total Questions:{" "}
            <strong>{test.question_count}</strong>
          </p>

          <p>
            Topics:{" "}
            <strong>
              {test.topics?.join(", ") || "Mathematics"}
            </strong>
          </p>

          <p className="helper">
            Your answers will be saved automatically
            under your logged-in student account.
          </p>

          <button
            type="button"
            className="button primary full"
            disabled={test.questions.length === 0}
            onClick={() => {
              setStarted(true);
              setError("");
            }}
          >
            Start Test
          </button>

          <p className="helper">
            Each answer can be submitted only once.
            Refreshing resumes from your saved answers.
          </p>
        </section>
      )}

      {/* Mathematics question */}
      {started && question && (
        <section className="panel assessment-panel">
          <div className="progress-row">
            <strong>
              Question {index + 1} of{" "}
              {test?.question_count}
            </strong>

            <span className="difficulty">
              {question.topic_id}
              {" · "}
              {question.difficulty}
            </span>
          </div>

          <div className="question-area">
            <h2>{question.statement}</h2>
          </div>

          {/* Answer options */}
          <div className="options">
            {question.options.map((option, i) => (
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
                  {option.text}
                </span>
              </button>
            ))}
          </div>

          {/* Submit answer */}
          {!feedback ? (
            <button
              type="button"
              className="button primary full"
              disabled={!selected || busy}
              onClick={submit}
            >
              {busy
                ? "Saving Answer..."
                : "Submit Answer"}
            </button>
          ) : (
            /* AI / Rule-based feedback */
            <div className="feedback-box review">
              <strong>
                {feedback.correct
                  ? "Correct!"
                  : "Review your answer"}
              </strong>

              <p>{feedback.feedback}</p>
              {feedback.explanation && !feedback.feedback.includes(feedback.explanation) && <p>{feedback.explanation}</p>}
              {feedback.corrective_guidance && <p>Learning tip: {feedback.corrective_guidance}</p>}

              {!feedback.correct && (
                <p>
                  Correct answer:{" "}
                  {feedback.correct_answer}
                </p>
              )}

              {!feedback.correct &&
                feedback.suspected_misconception && (
                  <p className="helper">
                    Possible misconception:{" "}
                    {feedback.suspected_misconception}
                  </p>
                )}

              <button
                type="button"
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

      {/* Completed assessment */}
      {started && complete && test && (
        <section className="panel narrow finished">
          <h2>Test Completed!</h2>

          <p>
            You answered{" "}
            <strong>{saved?.correct ?? 0}</strong> of{" "}
            <strong>{test.question_count}</strong>{" "}
            questions correctly.
          </p>

          <p>
            Your answers have been saved in Supabase.
            Your teacher can view your results from
            the teacher dashboard.
          </p>

          <Link
            href="/student"
            className="button primary full"
          >
            Back to My Tests
          </Link>
        </section>
      )}
      {started && complete && saved && <AssessmentReview result={saved} />}
    </main>
  );
}
