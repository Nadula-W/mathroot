"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { backendApi } from "../../lib/backend-api";
type Group = { class_id: string; teacher_name: string | null };
type Test = { test_id: string; title: string; topics: string[]; difficulty: string; question_count: number; status: string; correct: number; incorrect: number; percentage: number; completed_at: string | null };
export default function StudentPage() {
  const [classes, setClasses] = useState<Group[]>([]), [tests, setTests] = useState<Test[]>([]), [results, setResults] = useState<Test[]>([]);
  const [selected, setSelected] = useState(""), [id, setId] = useState(""), [code, setCode] = useState("");
  const [loading, setLoading] = useState(true), [joining, setJoining] = useState(false), [testsLoading, setTestsLoading] = useState(false);
  const [error, setError] = useState(""), [message, setMessage] = useState("");
  useEffect(() => {
    let active = true;
    Promise.all([backendApi<Group[]>("/api/student/classes"), backendApi<Test[]>("/api/student/results")])
      .then(([groups, saved]) => { if (active) { setClasses(groups); setResults(saved); setSelected(groups[0]?.class_id || ""); } })
      .catch(e => { if (active) setError(e.message); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    let active = true;
    setTests([]);
    if (!selected) return;
    setTestsLoading(true);
    backendApi<Test[]>(`/api/tests?class_id=${encodeURIComponent(selected)}`)
      .then(data => { if (active) setTests(data); }).catch(e => { if (active) setError(e.message); })
      .finally(() => { if (active) setTestsLoading(false); });
    return () => { active = false; };
  }, [selected]);
  async function join() {
    setJoining(true); setError(""); setMessage("");
    try {
      const data = await backendApi<{ status: string }>("/api/classes/join", { method: "POST", body: JSON.stringify({ class_id: id.trim(), join_code: code.trim() }) });
      setClasses(await backendApi<Group[]>("/api/student/classes")); setSelected(id.trim()); setCode("");
      setMessage(data.status === "already_enrolled" ? "You are already enrolled in this class." : "Class joined successfully.");
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to join class."); } finally { setJoining(false); }
  }
  return <main className="shell student-shell">
    <section className="section-head"><div className="eyebrow">STUDENT WORKSPACE</div><h1>My Mathematics Tests</h1><p>Your classes, assessments and saved feedback.</p></section>
    {error && <p className="alert" role="alert">{error}</p>}{message && <p className="alert soft" role="status">{message}</p>}
    <section className="panel"><h2>Join a Class</h2><div className="form-grid">
      <label className="field"><span>Class ID</span><input value={id} maxLength={64} onChange={e => setId(e.target.value)} /></label>
      <label className="field"><span>Teacher join code</span><input value={code} maxLength={128} onChange={e => setCode(e.target.value)} /></label></div>
      <button className="button primary" disabled={joining || !id.trim() || !code.trim()} onClick={join}>{joining ? "Joining..." : "Join Class"}</button></section>
    <section className="panel"><h2>My Classes</h2>{loading ? <p role="status">Loading classes...</p> : classes.length === 0 ? <p>Join your teacher’s class using its ID and code.</p> : classes.map(group => <div className="test-entry" key={group.class_id}><div><strong>{group.class_id}</strong><p>{group.teacher_name || "Teacher"}</p></div><button className="button" aria-pressed={selected === group.class_id} onClick={() => { setError(""); setSelected(group.class_id); }}>View Tests</button></div>)}</section>
    <section className="panel"><h2>Available Tests {selected && `— ${selected}`}</h2>{testsLoading ? <p role="status">Loading tests...</p> : !selected ? <p>Select a joined class.</p> : tests.length === 0 ? <p>No tests assigned yet.</p> : tests.map(test => <div className="test-entry" key={test.test_id}><div><h3>{test.title}</h3><p>{test.topics.join(", ")} · {test.difficulty} · {test.question_count} questions · {test.status}</p></div><Link className="button primary" href={`/student/test/${test.test_id}`}>{test.status === "Completed" ? "View Results" : test.status === "In Progress" ? "Continue Test" : "Start Test"}</Link></div>)}</section>
    <section className="panel"><h2>My Results</h2>{loading ? <p>Loading results...</p> : results.length === 0 ? <p>Completed tests will appear here.</p> : results.map(test => <div className="test-entry" key={test.test_id}><div><h3>{test.title}</h3><p>{test.correct}/{test.question_count} ({test.percentage}%) · {test.correct} correct · {test.incorrect} incorrect</p><p>{test.completed_at && new Date(test.completed_at).toLocaleString()}</p></div><Link className="button" href={`/student/test/${test.test_id}`}>View detailed feedback</Link></div>)}</section>
  </main>;
}
