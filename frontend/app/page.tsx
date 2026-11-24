const modules = [
  { name: "Transaction ingestion", state: "Foundation next", detail: "Synthetic and licensed public transaction data" },
  { name: "Fraud intelligence", state: "Not implemented", detail: "Behavioral features and XGBoost risk scoring" },
  { name: "AML network analysis", state: "Not implemented", detail: "Entity graph and GraphSAGE experimentation" },
  { name: "Risk & alerts", state: "Not implemented", detail: "Explainable prioritization for human review" },
];

export default function Home() {
  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand-mark">F</div>
        <div><strong>FININT</strong><span> / INVESTIGATOR WORKSPACE</span></div>
        <div className="env">ACADEMIC PROTOTYPE</div>
      </header>

      <section className="hero">
        <p className="eyebrow">FINANCIAL CRIME INTELLIGENCE</p>
        <h1>Banking Fraud <em>&</em><br />AML Intelligence</h1>
        <p className="intro">A unified workspace for transaction risk signals, suspicious financial networks, and investigation workflows.</p>
        <div className="hero-note"><span className="pulse" /> FOUNDATION BUILD · CONNECTORS NOT YET CONFIGURED</div>
      </section>

      <section className="section-head">
        <div><p className="eyebrow">SYSTEM OVERVIEW</p><h2>Platform modules</h2></div>
        <span className="counter">04 MODULES</span>
      </section>

      <section className="module-grid">
        {modules.map((module, index) => (
          <article className="module" key={module.name}>
            <div className="module-index">0{index + 1}</div>
            <div className="module-state">{module.state}</div>
            <h3>{module.name}</h3>
            <p>{module.detail}</p>
          </article>
        ))}
      </section>

      <footer>
        <span>FININT / INTERNAL SYSTEM</span>
        <span>Risk indicators support investigation; they are not proof of wrongdoing.</span>
      </footer>
    </main>
  );
}
