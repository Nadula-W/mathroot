"use client";
import { useLanguage } from "../lib/i18n/LanguageProvider";
import Link from "next/link";

export default function Home() {
  const { t } = useLanguage();
  return (
    <main className="shell">
      <header className="topbar">
        <Link href="/" className="logo"><span className="logo-icon">∑</span>MathRoot <span>AI</span></Link>
        <span className="topbar-tag">{t("O/L Mathematics \u00b7 Development demo")}</span>
      </header>

      <section className="hero">
        <div className="eyebrow">{t("BECS 32253 \u00b7 Intelligent Systems")}</div>
        <h1>{t("Discover the idea behind")}{" "}<em>{t("the mistake.")}</em></h1>
        <p className="lead">{t("A focused mathematics assessment experience for Sri Lankan O/L students, with teaching recommendations for tuition classes.")}</p>
      </section>

      <section className="choice-grid">
        <Link href="/student" className="choice-card">
          <span className="choice-symbol">01</span>
          <div><h2>{t("Student assessment")}</h2><p>{t("Take your teacher’s Mathematics tests, view explanations and review your progress.")}</p></div>
          <span className="choice-arrow">↗</span>
        </Link>
        <Link href="/teacher" className="choice-card">
          <span className="choice-symbol">02</span>
          <div><h2>{t("Teacher overview")}</h2><p>{t("See submitted answers, error patterns, and topic-specific corrective teaching suggestions.")}</p></div>
          <span className="choice-arrow">↗</span>
        </Link>
      </section>

      <div className="note"><strong>{t("How it works:")}</strong> {t("Questions are checked mathematically. AI-assisted feedback uses manual fallback when AI is unavailable. Use your own student or approved teacher account.")}</div>
      <footer className="footer">{t("MathRoot AI \u00b7 University project prototype \u00b7 Built for desktop and mobile")}</footer>
    </main>
  );
}
