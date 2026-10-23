
"use client";
import { backendApi } from "../../lib/backend-api";
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

async function jsonRequest<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const path = url.startsWith("/backend/")
    ? url.slice("/backend".length)
    : url;

  return backendApi<T>(path, options);
}


export default function TestCreator() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selected, setSelected] = useState<string[]>(["binomial"]);
  const [classId, setClassId] = useState("");
  const [title, setTitle] = useState("O/L Mathematics Practice Test");
  const [count, setCount] = useState(3);
  const [difficulty, setDifficulty] = useState("easy");
  const [classes, setClasses] = useState<{ class_id: string }[]>([]);
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

  useEffect(() => {
    const load = () => { backendApi<{ class_id: string }[]>("/api/classes").then(setClasses).catch(e => setError(e.message)); };
    load(); window.addEventListener("assessments-changed", load);
    return () => window.removeEventListener("assessments-changed", load);
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

      setMessage(`Test created: ${created.title}`);
      window.dispatchEvent(new Event("assessments-changed"));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Creation failed.");
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
          <select value={classId} onChange={e => setClassId(e.target.value)}><option value="">Select your class</option>{classes.map(c => <option key={c.class_id}>{c.class_id}</option>)}</select>
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
          busy || !classId ||
          selected.length === 0 ||
          !Number.isInteger(count) ||
          count < 1 ||
          count > 10
        }
      >
        {busy ? "Working..." : "Generate Test"}
      </button>

    </section>
  );
}
