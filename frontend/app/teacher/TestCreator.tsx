
"use client";

import { useEffect, useState } from "react";

type Topic = {
  id: string;
  name: string;
  owner: string;
  ready: boolean;
};

type TestInfo = {
  test_id: string;
  title: string;
  class_id: string;
  question_count: number;
  topics: string[];
};

type Results = TestInfo & {
  student_count: number;
  answers_submitted: number;
  topics_results: {
    topic_id: string;
    answers: number;
    correct: number;
    misconceptions: {
      code: string;
      count: number;
      recommendation: string;
    }[];
  }[];
  students: {
    student_id: string;
    answered: number;
    correct: number;
    misconceptions: { code: string; count: number }[];
  }[];
};

async function jsonRequest<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(url, {
    cache: "no-store",
    ...options,
  });

  const body = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : `Request failed: ${response.status}`
    );
  }

  return body as T;
}

export default function TestCreator() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selected, setSelected] = useState<string[]>(["binomial"]);
  const [classId, setClassId] = useState("demo-class");
  const [title, setTitle] = useState("O/L Mathematics Practice Test");
  const [count, setCount] = useState(3);
  const [difficulty, setDifficulty] = useState("easy");
  const [tests, setTests] = useState<TestInfo[]>([]);
  const [results, setResults] = useState<Results | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    jsonRequest<Topic[]>("/backend/api/topics")
      .then(setTopics)
      .catch(() =>
        setError("Cannot load topics. Check backend port 8000.")
      );
  }, []);

  function toggle(topicId: string) {
    setSelected((previous) =>
      previous.includes(topicId)
        ? previous.filter((id) => id !== topicId)
        : [...previous, topicId]
    );
  }

  async function createTest() {
    if (!classId.trim() || !title.trim() || selected.length === 0) {
      setError("Enter class ID, title and select a topic.");
      return;
    }

    setBusy(true);
    setError("");
    setMessage("");
    setResults(null);

    try {
      const created = await jsonRequest<TestInfo>(
        "/backend/api/tests",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: title.trim(),
            class_id: classId.trim(),
            topic_ids: selected,
            questions_per_topic: count,
            difficulty,
          }),
        }
      );

      setTests((previous) => [created, ...previous]);
      setMessage(`Test created: ${created.title}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Creation failed.");
    } finally {
      setBusy(false);
    }
  }

  async function loadTests() {
    if (!classId.trim()) {
      setError("Enter a class ID.");
      return;
    }

    setBusy(true);
    setError("");

    try {
      const data = await jsonRequest<TestInfo[]>(
        `/backend/api/tests?class_id=${encodeURIComponent(
          classId.trim()
        )}`
      );

      setTests(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Loading failed.");
    } finally {
      setBusy(false);
    }
  }

  async function loadResults(testId: string) {
    setBusy(true);
    setError("");

    try {
      const data = await jsonRequest<Results>(
        `/backend/api/tests/${testId}/results`
      );
      setResults(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Loading failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel" style={{ marginBottom: 24 }}>
      <div className="panel-kicker">Teacher Assessment Builder</div>
      <h2>Create Mathematics Test</h2>

      {error && <div className="alert">{error}</div>}
      {message && <div className="alert soft">{message}</div>}

      <div className="form-grid">
        <label className="field">
          <span>Class ID</span>
          <input
            value={classId}
            maxLength={64}
            onChange={(e) => setClassId(e.target.value)}
          />
        </label>

        <label className="field">
          <span>Test Title</span>
          <input
            value={title}
            maxLength={100}
            onChange={(e) => setTitle(e.target.value)}
          />
        </label>
      </div>

      <h3>Select Mathematics Topics</h3>

      <div className="topic-choices">
        {topics.map((topic) => (
          <label className="topic-choice" key={topic.id}>
            <input
              type="checkbox"
              checked={selected.includes(topic.id)}
              disabled={!topic.ready || busy}
              onChange={() => toggle(topic.id)}
            />
            <span>
              {topic.name}
              <small>
                {" "}({topic.owner}) —{" "}
                {topic.ready ? "Ready" : "Coming soon"}
              </small>
            </span>
          </label>
        ))}
      </div>

      <div className="form-grid">
        <label className="field">
          <span>Questions per Topic</span>
          <input
            type="number"
            min={1}
            max={10}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
          />
        </label>

        <label className="field">
          <span>Difficulty</span>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </label>
      </div>

      <button
        className="button primary"
        onClick={createTest}
        disabled={
          busy ||
          selected.length === 0 ||
          !Number.isInteger(count) ||
          count < 1 ||
          count > 10
        }
      >
        {busy ? "Working..." : "Generate Test"}
      </button>

      <button
        className="button ghost"
        style={{ marginLeft: 12 }}
        onClick={loadTests}
        disabled={busy}
      >
        Load Class Tests
      </button>

      {tests.length > 0 && (
        <div style={{ marginTop: 26 }}>
          <h3>Created Tests</h3>

          {tests.map((test) => {
            const path = `/student/test/${test.test_id}`;
            const link =
              typeof window === "undefined"
                ? ""
                : `${window.location.origin}${path}`;

            return (
              <div className="test-entry" key={test.test_id}>
                <div>
                  <strong>{test.title}</strong>
                  <p className="muted">
                    {test.question_count} questions
                    {" · "}
                    {test.topics.join(", ")}
                  </p>
                </div>

                <div className="test-buttons">
                  <a href={path} target="_blank" rel="noreferrer">
                    Student Link
                  </a>

                  <button
                    onClick={() =>
                      navigator.clipboard.writeText(link)
                    }
                  >
                    Copy Link
                  </button>

                  <button
                    onClick={() => loadResults(test.test_id)}
                    disabled={busy}
                  >
                    Results
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {results && (
        <div className="results-area">
          <h3>Results — {results.title}</h3>
          <p>
            {results.student_count} students ·{" "}
            {results.answers_submitted} submitted answers
          </p>

          <h3>Topic Feedback</h3>

          {results.topics_results.map((topic) => (
            <div className="test-entry" key={topic.topic_id}>
              <div>
                <strong>{topic.topic_id}</strong>
                <p>
                  {topic.correct}/{topic.answers} correct answers
                </p>

                {topic.misconceptions.map((m) => (
                  <p className="muted" key={m.code}>
                    {m.code}: {m.count} wrong-answer events.
                    {" "}{m.recommendation}
                  </p>
                ))}
              </div>
            </div>
          ))}

          <h3>Individual Student Feedback</h3>

          {results.students.map((s) => (
            <p key={s.student_id}>
              <strong>{s.student_id}:</strong>{" "}
              {s.correct}/{s.answered} correct
              {s.misconceptions.length > 0 && (
                <>
                  {" · Possible difficulties: "}
                  {s.misconceptions
                    .map((m) => `${m.code} (${m.count})`)
                    .join(", ")}
                </>
              )}
            </p>
          ))}

          <p className="helper">
            Misconceptions are preliminary error signals,
            not confirmed diagnoses.
          </p>
        </div>
      )}
    </section>
  );
}
