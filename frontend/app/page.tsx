import Link from "next/link";

export default function Home() {
  return (
    <main className="shell">
      <header className="topbar">
        <Link href="/" className="logo"><span className="logo-icon">∑</span>MathRoot <span>AI</span></Link>
        <span className="topbar-tag">O/L Mathematics · Development demo</span>
      </header>

      <section className="hero">
        <div className="eyebrow">BECS 32253 · Intelligent Systems</div>
        <h1>Discover the idea behind <em>the mistake.</em></h1>
        <p className="lead">A focused mathematics assessment experience for Sri Lankan O/L students, with teaching recommendations for tuition classes.</p>
      </section>

      <section className="choice-grid">
        <Link href="/student" className="choice-card">
          <span className="choice-symbol">01</span>
          <div><h2>Student assessment</h2><p>Answer five generated Binomial Expressions questions. See explanations and get follow-up practice.</p></div>
          <span className="choice-arrow">↗</span>
        </Link>
        <Link href="/teacher" className="choice-card">
          <span className="choice-symbol">02</span>
          <div><h2>Teacher overview</h2><p>See submitted answers, error patterns, and topic-specific corrective teaching suggestions.</p></div>
          <span className="choice-arrow">↗</span>
        </Link>
      </section>

      <div className="note"><strong>Milestone 2:</strong> The backend generates questions using verified rules. LLM generation, secure accounts, and advanced AI diagnosis are planned for later phases. Use test IDs only.</div>
      <footer className="footer">MathRoot AI · University project prototype · Built for desktop and mobile</footer>
    </main>
  );
}
