"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";

import { useEffect, useState } from "react";
import Link from "next/link";
import { backendApi } from "../../lib/backend-api";
type Group = { class_id: string; teacher_name: string | null };
type Test = { test_id: string; title: string; topics: string[]; difficulty: string; question_count: number; status: string; correct: number; incorrect: number; percentage: number; completed_at: string | null };
export default function StudentPage() {
  const { t, topic, errorText, locale } = useLanguage();
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
    <section className="section-head"><div className="eyebrow">{t("STUDENT WORKSPACE")}</div><h1>{t("My Mathematics Tests")}</h1><p>{t("Your classes, assessments and saved feedback.")}</p></section>
    {error && <p className="alert" role="alert">{errorText(error)}</p>}{message && <p className="alert soft" role="status">{errorText(message)}</p>}
    <section className="panel"><h2>{t("Join a Class")}</h2><div className="form-grid">
      <label className="field"><span>{t("Class ID")}</span><input value={id} maxLength={64} onChange={e => setId(e.target.value)} /></label>
      <label className="field"><span>{t("Teacher join code")}</span><input value={code} maxLength={128} onChange={e => setCode(e.target.value)} /></label></div>
      <button className="button primary" disabled={joining || !id.trim() || !code.trim()} onClick={join}>{t(joining ? "Joining..." : "Join Class")}</button></section>
    <section className="panel"><h2>{t("My Classes")}</h2>{loading ? <p role="status">{t("Loading classes...")}</p> : classes.length === 0 ? <p>{t("Join your teacher\u2019s class using its ID and code.")}</p> : classes.map(group => <div className="test-entry" key={group.class_id}><div><strong>{group.class_id}</strong><p>{group.teacher_name || t("Teacher")}</p></div><button className="button" aria-pressed={selected === group.class_id} onClick={() => { setError(""); setSelected(group.class_id); }}>{t("View Tests")}</button></div>)}</section>
    <section className="panel"><h2>{t("Available Tests")} {selected && `— ${selected}`}</h2>{testsLoading ? <p role="status">{t("Loading tests...")}</p> : !selected ? <p>{t("Select a joined class.")}</p> : tests.length === 0 ? <p>{t("No tests assigned yet.")}</p> : tests.map(test => <div className="test-entry" key={test.test_id}><div><h3>{test.title}</h3><p>{test.topics.map(topic).join(", ")} · {t(test.difficulty === "easy" ? "Easy" : test.difficulty === "medium" ? "Medium" : "Hard")} · {t("{count} questions", { count: test.question_count })} · {t(test.status)}</p></div><Link className="button primary" href={`/student/test/${test.test_id}`}>{t(test.status === "Completed" ? "View Results" : test.status === "In Progress" ? "Continue Test" : "Start Test")}</Link></div>)}</section>
    <section className="panel"><h2>{t("My Results")}</h2>{loading ? <p>{t("Loading results...")}</p> : results.length === 0 ? <p>{t("Completed tests will appear here.")}</p> : results.map(test => <div className="test-entry" key={test.test_id}><div><h3>{test.title}</h3><p>{test.correct}/{test.question_count} ({test.percentage}%) · {t("{correct} correct \u00b7 {incorrect} incorrect", { correct: test.correct, incorrect: test.incorrect })}</p><p>{test.completed_at && new Date(test.completed_at).toLocaleString(locale)}</p></div><Link className="button" href={`/student/test/${test.test_id}`}>{t("View detailed feedback")}</Link></div>)}</section>
  </main>;
}
