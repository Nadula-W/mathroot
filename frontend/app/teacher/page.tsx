"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";

import ClassManager from "./ClassManager";
import TestCreator from "./TestCreator";
import TestManager from "./TestManager";
export default function TeacherPage() {
  const { t } = useLanguage();
  return <main className="shell teacher-shell"><section className="section-head"><div className="eyebrow">{t("TEACHER WORKSPACE")}</div><h1>{t("From answers to teaching actions.")}</h1><p>{t("Create Mathematics tests and review your students\u2019 progress.")}</p></section><ClassManager /><TestCreator /><TestManager /></main>;
}
