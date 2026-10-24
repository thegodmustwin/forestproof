import Link from "next/link";
import { DemoNotice } from "@/components/demo-notice";
import { OutcomeGraph } from "@/components/outcome-graph";
import { StatusChip } from "@/components/status-chip";
import { cases, demoMode, monitoredArea, observations } from "@/lib/demo";

export default function CommandCenterPage() {
  return (
    <div className="page">
      <div className="topline">
        <div>
          <p className="eyebrow">ForestProof · Aberdare Monitor</p>
          <h1>Make the response as visible as the signal.</h1>
          <p className="lede">A case-operating system for documenting environmental observations, responsible review, authorised interventions, and follow-up—not for declaring wrongdoing from a map.</p>
        </div>
        <span className="demo-chip">{demoMode.label}</span>
      </div>
      <DemoNotice />
      <section className="metric-grid" aria-label="Demo operations summary">
        <article className="metric"><p className="metric-label">Reviewable observations</p><p className="metric-value">{observations.length}</p><p className="metric-help">Synthetic records awaiting or illustrating human review.</p></article>
        <article className="metric metric-alert"><p className="metric-label">Open review records</p><p className="metric-value">{cases.filter((item) => item.status !== "CLOSED").length}</p><p className="metric-help">Demo cases with no real-world operational meaning.</p></article>
        <article className="metric"><p className="metric-label">Verified outcomes</p><p className="metric-value">0</p><p className="metric-help">No environmental outcomes are asserted in demo mode.</p></article>
        <article className="metric"><p className="metric-label">Source integrity</p><p className="metric-value">100<span style={{ fontSize: 18 }}>%</span></p><p className="metric-help">Fixture provenance retained for every demo record.</p></article>
      </section>
      <section className="dashboard-grid">
        <article className="card">
          <div className="card-head"><div><h2>Response queue</h2><p className="card-subtitle">What needs a transparent, authorised next step?</p></div><Link className="link-arrow" href="/operations">View operations →</Link></div>
          <div className="card-body">
            {cases.map((item) => (
              <Link href={`/cases/${item.id}`} className="case-row" key={item.id}>
                <div><div className="case-title">{item.title}</div><div className="case-meta">{item.id} · Owner: {item.owner} · {item.evidenceCount} evidence records</div></div>
                <div style={{ textAlign: "right" }}><StatusChip status={item.status} /><div className="priority" style={{ marginTop: 7 }}>{item.priority} triage</div></div>
              </Link>
            ))}
          </div>
        </article>
        <article className="card">
          <div className="card-head"><div><h2>Monitoring context</h2><p className="card-subtitle">Scope is intentionally explicit.</p></div></div>
          <div className="card-body">
            <p style={{ marginTop: 0, fontWeight: 800, fontSize: 15 }}>{monitoredArea.name}</p>
            <p className="detail-note">{monitoredArea.description}</p>
            <div className="facts" style={{ marginBottom: 0 }}><div className="fact"><span className="fact-label">Geography</span><span>Kenya · Aberdare context</span></div><div className="fact"><span className="fact-label">Boundary status</span><span>{monitoredArea.areaLabel}</span></div><div className="fact"><span className="fact-label">Decision authority</span><span>Qualified humans and lawful institutions</span></div></div>
            <Link className="button" style={{ marginTop: 18 }} href="/monitor/aberdare">Open monitor</Link>
          </div>
        </article>
      </section>
      <section className="card section-gap">
        <div className="card-head"><div><h2>Forest Intervention Outcome Graph</h2><p className="card-subtitle">The durable record connects a source observation to a verified, bounded response—not a speculative alert count.</p></div><Link className="link-arrow" href="/outcomes">Explore graph →</Link></div>
        <div className="card-body"><OutcomeGraph /></div>
      </section>
    </div>
  );
}
