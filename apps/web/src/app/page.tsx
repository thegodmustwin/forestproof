"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DemoNotice } from "@/components/demo-notice";
import { OutcomeGraph } from "@/components/outcome-graph";
import { StatusChip } from "@/components/status-chip";
import { loadObservations } from "@/lib/api";
import { demoMode, monitoredArea } from "@/lib/demo";
import { useCaseQueue } from "@/lib/use-case-queue";

function FieldContour() {
  return <svg viewBox="0 0 480 350" className="field-contour" fill="none" aria-hidden="true">
    <path d="M-80 285C10 110 105 385 220 180S360 210 520-20M-70 310C15 130 120 400 235 200S390 245 540 10M-60 335C20 150 135 415 250 220S420 280 560 40M-50 360C25 170 150 430 265 240S450 315 580 70M-40 385C30 190 165 445 280 260S480 350 600 100M-30 410C35 210 180 460 295 280S510 385 620 130M-20 435C40 230 195 475 310 300S540 420 640 160" stroke="currentColor" strokeWidth="1" />
    <circle cx="270" cy="157" r="44" stroke="currentColor" strokeDasharray="3 6" />
    <circle cx="270" cy="157" r="5" fill="currentColor" stroke="none" />
  </svg>;
}

export default function CommandCenterPage() {
  const { state, retry } = useCaseQueue();
  const [observationCount, setObservationCount] = useState<number | null>(null);
  useEffect(() => {
    let active = true;
    void loadObservations().then(({ items }) => { if (active) setObservationCount(items.length); }).catch(() => {});
    return () => { active = false; };
  }, []);
  const openCases = state.status === "ready" ? state.cases.filter((item) => item.status !== "CLOSED") : null;

  return <div className="page command-center">
    <div className="workspace-heading"><p className="eyebrow">Aberdare / demonstration workspace</p><span className="demo-chip">{demoMode.label}</span></div>
    <section className="command-hero" aria-labelledby="command-title">
      <div className="command-intro">
        <p className="hero-kicker">A clearer path from signal to response</p>
        <h1 id="command-title">From observation to action.</h1>
        <p className="lede">Review an observation, document what you learn, and keep track of the response and follow-up. Every step starts with human review.</p>
        <div className="button-row dashboard-actions"><Link className="button" href="/monitor/aberdare">Explore demo observations →</Link><Link className="button secondary" href="/operations">View demo cases</Link></div>
      </div>
      <aside className="field-note" aria-label="How the review workflow works">
        <FieldContour />
        <p className="field-note-label">The review trail</p>
        <h2>A record worth following.</h2>
        <p>One observation. A responsible reviewer. A documented next step.</p>
        <ol className="review-trail"><li><span>01</span>Observe</li><li><span>02</span>Review</li><li><span>03</span>Respond</li><li><span>04</span>Follow up</li></ol>
      </aside>
    </section>
    <DemoNotice />
    <section className="metric-grid dashboard-metrics" aria-label="Demo operations summary">
      <article className="metric"><p className="metric-label">Demo observations</p><p className="metric-value">{observationCount ?? "—"}</p><p className="metric-help">{observationCount === null ? "Connect to the API to load records." : "Synthetic records available for human review."}</p></article>
      <article className="metric"><p className="metric-label">Open review records</p><p className="metric-value">{openCases?.length ?? "—"}</p><p className="metric-help">{openCases ? "Saved synthetic cases that are not closed." : "Loading or unable to reach saved cases."}</p></article>
      <article className="metric"><p className="metric-label">Environmental outcomes</p><p className="metric-value metric-value-text">Not measured</p><p className="metric-help">This demo makes no claim of conservation impact.</p></article>
      <article className="metric"><p className="metric-label">Source status</p><p className="metric-value metric-value-text">Demo</p><p className="metric-help">A verified live observation feed is not yet connected.</p></article>
    </section>
    <div className="dashboard-grid">
      <section className="card case-queue-card"><div className="card-head"><div><p className="section-eyebrow">The next step</p><h2>Open cases</h2><p className="card-subtitle">Saved demo cases available for review.</p></div><Link className="link-arrow" href="/operations">View all cases →</Link></div><div className="card-body">
        {state.status === "loading" && <p className="detail-note queue-state" role="status">Loading saved cases…</p>}
        {state.status === "unavailable" && <div className="queue-state" role="status"><p className="detail-note">Saved cases are unavailable.</p><button className="button secondary" onClick={retry}>Try again</button></div>}
        {openCases && openCases.length === 0 && <div className="queue-state"><span className="empty-record-mark" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="1.3"><path d="M8 4h11l6 6v18H8V4Z" /><path d="M19 4v7h6M12 17h9m-9 5h6" /></svg></span><p className="detail-note">No open demo cases yet.</p><Link className="link-arrow" href="/monitor/aberdare">Review a demo observation →</Link></div>}
        {openCases?.slice(0, 5).map((item) => <Link href={`/cases/${encodeURIComponent(item.id)}`} className="case-row" key={item.id}><div><div className="case-title">{item.title}</div><div className="case-meta">{item.id} · Owner: {item.owner}</div></div><StatusChip status={item.status} /></Link>)}
      </div></section>
      <section className="card monitoring-context"><div className="card-head"><div><p className="section-eyebrow">Know the scope</p><h2>Monitoring context</h2><p className="card-subtitle">Scope is intentionally explicit.</p></div></div><div className="card-body"><p className="context-area-name">{monitoredArea.name}</p><p className="detail-note">{monitoredArea.description}</p><div className="facts"><div className="fact"><span className="fact-label">Geography</span><span>Kenya · Aberdare context</span></div><div className="fact"><span className="fact-label">Boundary status</span><span>{monitoredArea.areaLabel}</span></div><div className="fact"><span className="fact-label">Decision authority</span><span>Qualified humans and lawful institutions</span></div></div><Link className="link-arrow context-link" href="/monitor/aberdare">Open monitor</Link></div></section>
    </div>
    <section className="card section-gap outcome-summary"><div className="card-head"><div><p className="section-eyebrow">A connected history</p><h2>Forest Intervention Outcome Graph</h2><p className="card-subtitle">The durable record connects a source observation to a verified, bounded response—not a speculative alert count.</p></div><Link className="link-arrow" href="/outcomes">Explore graph →</Link></div><div className="card-body"><OutcomeGraph /></div></section>
  </div>;
}
