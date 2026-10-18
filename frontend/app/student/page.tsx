
"use client";

import Link from "next/link";
import { useState } from "react";

type Test = {
  test_id: string;
  title: string;
  class_id: string;
  question_count: number;
  topics: string[];
};

export default function StudentPage() {
  const [classId, setClassId] = useState("");
  const [tests, setTests] = useState<Test[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");

  async function loadTests(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (!classId.trim()) return;

    setLoading(true);
    setError("");
    setTests([]);
    setSearched(false);

    try {
      const response = await fetch(
        `/backend/api/tests?class_id=${encodeURIComponent(
          classId.trim()
        )}`,
        { cache: "no-store" }
      );

      if (!response.ok) {
        throw new Error(
          `Cannot load class tests (HTTP ${response.status})`
        );
      }

      const data: Test[] = await response.json();

      setTests(data);
      setSearched(true);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load tests."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell student-shell">
      <header className="topbar">
        <Link href="/" className="logo">
          MathRoot AI
        </Link>
      </header>

      <section className="section-head">
        <div className="eyebrow">STUDENT WORKSPACE</div>
        <h1>My Mathematics Tests</h1>
        <p>
          Enter your class ID to find the assessments
          assigned by your teacher.
        </p>
      </section>

      <section className="panel narrow">
        <h2>Find My Class</h2>

        <form onSubmit={loadTests}>
          <label className="field">
            <span>Class ID</span>
            <input
              value={classId}
              onChange={(e) => setClassId(e.target.value)}
              placeholder="Example: demo2"
              maxLength={64}
              required
            />
          </label>

          <button
            type="submit"
            className="button primary full"
            disabled={loading}
          >
            {loading ? "Loading..." : "Find Tests"}
          </button>
        </form>

        {error && (
          <div className="alert" role="alert">
            {error}
          </div>
        )}
      </section>

      {searched && (
        <section className="panel" style={{ marginTop: 24 }}>
          <h2>Available Tests</h2>

          {tests.length === 0 ? (
            <p>
              No tests found for class "{classId}".
              Ask your teacher to create a test.
            </p>
          ) : (
            <div style={{ display: "grid", gap: 16 }}>
              {tests.map((test) => (
                <div
                  key={test.test_id}
                  className="test-entry"
                >
                  <div>
                    <h3>{test.title}</h3>

                    <p className="muted">
                      {test.question_count} Questions
                    </p>

                    <p className="muted">
                      Topics: {test.topics.join(", ")}
                    </p>
                  </div>

                  <Link
                    className="button primary"
                    href={`/student/test/${test.test_id}`}
                  >
                    Start Test
                  </Link>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </main>
  );
}
