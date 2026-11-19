"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DemoNotice } from "@/components/demo-notice";
import { OutcomeGraph } from "@/components/outcome-graph";
import { StatusChip } from "@/components/status-chip";
import { loadObservations } from "@/lib/api";
import { demoMode, monitoredArea } from "@/lib/demo";
import { useCaseQueue } from "@/lib/use-case-queue";

export default function CommandCenterPage() {
  const { state, retry } = useCaseQueue();
  const [observationCount, setObservationCount] = useState<number | null>(null);
  useEffect(() => {
    let active = true;
    void loadObservations().then(({ items }) => { if (active) setObservationCount(items.length); }).catch(() => {});
    return () => { active = false; };
  }, []);
  const openCases = state.status === "ready" ? state.cases.filter((item) => item.status !== "CLOSED") : null;
  const nextCase = openCases?.[0];

  return <div className="page command-center">
    <div className="workspace-heading"><p className="eyebrow">Living Atlas / Aberdare research</p><span className="demo-chip">{demoMode.label}</span></div>
    <section className="command-hero" aria-labelledby="command-title">
      <div className="command-intro">
        <p className="hero-kicker">Observe. Review. Respond.</p>
        <h1 id="command-title">From observation to action.</h1>
        <p className="lede">Review an observation, document what you learn, and keep track of the response and follow-up. Every step starts with human review.</p>
        <div className="button-row dashboard-actions"><Link className="button" href="/monitor/aberdare">Explore demo observations →</Link><Link className="button secondary" href="/operations">View demo cases</Link></div>
      </div>
      <aside className="field-note" aria-label="Next saved case">
        <p className="field-note-label">Continue a saved review</p>
        {nextCase ? <>
          <StatusChip status={nextCase.status} />
          <h2>{nextCase.title}</h2>
          <p>{nextCase.id} · {nextCase.owner}</p>
          <Link className="button" href={`/cases/${encodeURIComponent(nextCase.id)}`}>Open this case →</Link>
        </> : <>
          <h2>A record worth following.</h2>
          <p>{state.status === "loading" ? "Loading your saved demo reviews…" : state.status === "unavailable" ? "Saved reviews are unavailable. Reconnect to continue a case." : "Review a synthetic observation and give its next step a recorded owner."}</p>
          {state.status === "unavailable" ? <button className="button secondary" onClick={retry}>Try again</button> : <Link className="button secondary" href="/monitor/aberdare">Review a demo observation →</Link>}
        </>}
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
    <section className="card section-gap outcome-summary"><div className="card-head"><div><p className="section-eyebrow">A connected history</p><h2>Forest Intervention Outcome Graph</h2><p className="card-subtitle">Trace the source observation, review and follow-up recorded for a saved case.</p></div><Link className="link-arrow" href="/outcomes">Explore graph →</Link></div><div className="card-body"><OutcomeGraph /></div></section>
  </div>;
}
