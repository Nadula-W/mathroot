"use client";
import ClassManager from "./ClassManager";
import TestCreator from "./TestCreator";
import TestManager from "./TestManager";
export default function TeacherPage() {
  return <main className="shell teacher-shell"><section className="section-head"><div className="eyebrow">TEACHER WORKSPACE</div><h1>From answers to teaching actions.</h1><p>Create Mathematics tests and review your students’ progress.</p></section><ClassManager /><TestCreator /><TestManager /></main>;
}
