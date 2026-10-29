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

  return <div className="page">
    <div className="topline"><div><p className="eyebrow">ForestProof · Aberdare Monitor</p><h1>Make the response as visible as the signal.</h1><p className="lede">A case-operating system for documenting environmental observations, responsible review, authorised interventions, and follow-up—not for declaring wrongdoing from a map.</p></div><span className="demo-chip">{demoMode.label}</span></div>
    <DemoNotice />
    <section className="metric-grid" aria-label="Demo operations summary">
      <article className="metric"><p className="metric-label">Demo observations</p><p className="metric-value">{observationCount ?? "—"}</p><p className="metric-help">{observationCount === null ? "Connect to the API to load records." : "Synthetic records available for human review."}</p></article>
      <article className="metric metric-alert"><p className="metric-label">Open review records</p><p className="metric-value">{openCases?.length ?? "—"}</p><p className="metric-help">{openCases ? "Saved synthetic cases that are not closed." : "Loading or unable to reach saved cases."}</p></article>
      <article className="metric"><p className="metric-label">Verified outcomes</p><p className="metric-value">0</p><p className="metric-help">No environmental outcomes are asserted in demo mode.</p></article>
      <article className="metric"><p className="metric-label">Source status</p><p className="metric-value">Demo</p><p className="metric-help">A verified live observation feed is not yet connected.</p></article>
    </section>
    <div className="dashboard-grid">
      <section className="card"><div className="card-head"><div><h2>Response queue</h2><p className="card-subtitle">Saved demo cases needing a next step.</p></div><Link className="link-arrow" href="/operations">View operations →</Link></div><div className="card-body">
        {state.status === "loading" && <p className="detail-note" role="status">Loading saved cases…</p>}
        {state.status === "unavailable" && <div role="status"><p className="detail-note">Saved cases are unavailable.</p><button className="button secondary" onClick={retry}>Try again</button></div>}
        {openCases && openCases.length === 0 && <div><p className="detail-note">No open demo cases yet.</p><Link className="link-arrow" href="/monitor/aberdare">Review a demo observation →</Link></div>}
        {openCases?.slice(0, 5).map((item) => <Link href={`/cases/${encodeURIComponent(item.id)}`} className="case-row" key={item.id}><div><div className="case-title">{item.title}</div><div className="case-meta">{item.id} · Owner: {item.owner}</div></div><StatusChip status={item.status} /></Link>)}
      </div></section>
      <section className="card"><div className="card-head"><div><h2>Monitoring context</h2><p className="card-subtitle">Scope is intentionally explicit.</p></div></div><div className="card-body"><p style={{ marginTop: 0, fontWeight: 800, fontSize: 15 }}>{monitoredArea.name}</p><p className="detail-note">{monitoredArea.description}</p><div className="facts" style={{ marginBottom: 0 }}><div className="fact"><span className="fact-label">Geography</span><span>Kenya · Aberdare context</span></div><div className="fact"><span className="fact-label">Boundary status</span><span>{monitoredArea.areaLabel}</span></div><div className="fact"><span className="fact-label">Decision authority</span><span>Qualified humans and lawful institutions</span></div></div><Link className="button" style={{ marginTop: 18 }} href="/monitor/aberdare">Open monitor</Link></div></section>
    </div>
    <section className="card section-gap"><div className="card-head"><div><h2>Forest Intervention Outcome Graph</h2><p className="card-subtitle">The durable record connects a source observation to a verified, bounded response—not a speculative alert count.</p></div><Link className="link-arrow" href="/outcomes">Explore graph →</Link></div><div className="card-body"><OutcomeGraph /></div></section>
  </div>;
}
