"use client";
import { TranslationWarning, useLanguage } from "../../lib/i18n/LanguageProvider";
import type { Translatable } from "../../lib/i18n/core";

import { useEffect, useState } from "react";
import { backendApi } from "../../lib/backend-api";
import AssessmentReview, { SavedResult } from "../components/AssessmentReview";
type Test = { test_id: string; title: string; class_id: string; topics: string[]; difficulty: string; question_count: number; created_at: string | null; participant_count: number };
type Results = { title: string; enrolled_count: number; student_count: number; completed_count: number; average_score: number | null; highest_score: number | null; lowest_score: number | null; students: { student_id: string; full_name: string; status: string; correct: number; incorrect: number; percentage: number }[]; topics_results: { topic_id: string; misconceptions: (Translatable & { code: string; count: number; recommendation: string })[] }[] };
export default function TestManager() {
  const { t, topic: topicLabel, content, errorText, locale } = useLanguage();
  const [tests, setTests] = useState<Test[]>([]), [classes, setClasses] = useState<{ class_id: string }[]>([]);
  const [filter, setFilter] = useState(""), [error, setError] = useState(""), [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false), [results, setResults] = useState<Results | null>(null), [review, setReview] = useState<SavedResult | null>(null), [testId, setTestId] = useState("");
  async function reload() {
    setBusy(true); setError("");
    try { const [data, groups] = await Promise.all([backendApi<Test[]>("/api/teacher/tests"), backendApi<{ class_id: string }[]>("/api/classes")]); setTests(data); setClasses(groups); }
    catch (e) { setError(e instanceof Error ? e.message : "Unable to load tests."); } finally { setBusy(false); }
  }
  useEffect(() => { void reload(); const refresh = () => { void reload(); }; window.addEventListener("assessments-changed", refresh); return () => window.removeEventListener("assessments-changed", refresh); }, []);
  async function showResults(id: string) {
    setBusy(true); setError(""); setResults(null); setReview(null); setTestId(id);
    try { setResults(await backendApi<Results>(`/api/tests/${id}/results`)); } catch (e) { setError(e instanceof Error ? e.message : "Unable to load results."); } finally { setBusy(false); }
  }
  async function remove(test: Test) {
    if (!window.confirm(t("Delete “{title}”? This permanently deletes this test and all its student submissions and results.", { title: test.title }))) return;
    setBusy(true); setError("");
    try { await backendApi(`/api/tests/${test.test_id}`, { method: "DELETE" }); if (testId === test.test_id) { setResults(null); setReview(null); } setMessage("Test and its submissions deleted."); await reload(); }
    catch (e) { setError(e instanceof Error ? e.message : "Deletion failed."); } finally { setBusy(false); }
  }
  async function inspect(studentId: string) {
    setBusy(true); setError(""); setReview(null);
    try { setReview(await backendApi<SavedResult>(`/api/tests/${testId}/students/${studentId}`)); } catch (e) { setError(e instanceof Error ? e.message : "Unable to load answers."); } finally { setBusy(false); }
  }
  async function copy(id: string) {
    try { await navigator.clipboard.writeText(`${window.location.origin}/student/test/${id}`); setMessage("Student link copied. Students must join the class before opening it."); } catch { setError("Clipboard unavailable. Open the student link and copy its address."); }
  }
  return <section className="panel"><h2>{t("Manage Mathematics Tests")}</h2>
    <label className="field"><span>{t("Filter by class")}</span><select value={filter} onChange={e => setFilter(e.target.value)}><option value="">{t("All my classes")}</option>{classes.map(c => <option key={c.class_id}>{c.class_id}</option>)}</select></label>
    <button className="button" disabled={busy} onClick={reload}>{t("Reload Tests")}</button>
    {busy && <p role="status">{t("Loading...")}</p>}{error && <p className="alert" role="alert">{errorText(error)}</p>}{message && <p role="status">{errorText(message)}</p>}
    {!busy && tests.filter(t => !filter || t.class_id === filter).length === 0 && <p>{t("No tests in this selection. Create a class and generate a test above.")}</p>}
    {tests.filter(t => !filter || t.class_id === filter).map(test => <article className="test-entry" key={test.test_id}><div><h3>{test.title}</h3><p>{t("Class:")} {test.class_id} · {test.topics.map(topicLabel).join(", ")} · {t(test.difficulty === "easy" ? "Easy" : test.difficulty === "medium" ? "Medium" : "Hard")}</p><p>{t("{count} questions", { count: test.question_count })} · {t("{count} participating students", { count: test.participant_count })} · {test.created_at && new Date(test.created_at).toLocaleString(locale)}</p></div><div className="test-buttons"><button className="button" disabled={busy} onClick={() => showResults(test.test_id)}>{t("View Results")}</button><button className="button" onClick={() => copy(test.test_id)}>{t("Copy Student Link")}</button><a href={`/student/test/${test.test_id}`} className="text-link">{t("Student Link")}</a><button className="button" disabled={busy} onClick={() => remove(test)}>{t("Delete Test")}</button></div></article>)}
    {results && <div><h3>{t("Results \u2014 {title}", { title: results.title })}</h3><p>{t("{enrolled} enrolled \u00b7 {attempted} attempted \u00b7 {completed} completed", { enrolled: results.enrolled_count, attempted: results.student_count, completed: results.completed_count })}</p><p>{t("Completed scores: average {average}% \u00b7 highest {highest}% \u00b7 lowest {lowest}%", { average: results.average_score ?? "-", highest: results.highest_score ?? "-", lowest: results.lowest_score ?? "-" })}</p>
      {results.students.length === 0 && <p>{t("No submissions yet.")}</p>}
      {results.students.map(s => <article className="test-entry" key={s.student_id}><div><strong>{s.full_name === "Student" ? t("Student") : s.full_name}</strong><p>{t(s.status)} · {t("{correct} correct \u00b7 {incorrect} incorrect", { correct: s.correct, incorrect: s.incorrect })} · {s.percentage}%</p></div><button className="button" disabled={busy} onClick={() => inspect(s.student_id)}>{t("Inspect answers")}</button></article>)}
      <h3>{t("Common misconceptions and teaching actions")}</h3>{results.topics_results.map(topic => <div key={topic.topic_id}><h4>{topicLabel(topic.topic_id)}</h4>{topic.misconceptions.length === 0 && <p>{t("No misconception signals recorded.")}</p>}{topic.misconceptions.map(m => <p key={m.code}>{t(m.code)}: {t("{count} signals.", { count: m.count })} {content(m, "recommendation")}<TranslationWarning record={m} fields={["recommendation"]} /></p>)}</div>)}
    </div>}{review && <AssessmentReview result={review} />}
  </section>;
}
