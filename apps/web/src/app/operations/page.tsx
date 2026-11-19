"use client";

import { useState } from "react";
import Link from "next/link";
import { DemoNotice } from "@/components/demo-notice";
import { StatusChip } from "@/components/status-chip";
import { demoMode, formatDate } from "@/lib/demo";
import { useCaseQueue } from "@/lib/use-case-queue";

export default function OperationsPage() {
  const { state, retry } = useCaseQueue();
  const [view, setView] = useState("all");
  const cases = state.status === "ready" ? state.cases : [];
  const openCount = cases.filter((item) => item.status !== "CLOSED").length;
  const visibleCases = cases.filter((item) => view === "all" || (view === "open" ? item.status !== "CLOSED" : item.status === "CLOSED"));

  return <div className="page operations-desk">
    <div className="topline">
      <div><p className="eyebrow">Investigation desk / Case queue</p><h1>Every case has a next step.</h1><p className="lede">Find a saved review, see who owns it, and continue its recorded response.</p></div>
      <span className="demo-chip">{demoMode.label}</span>
    </div>
    <DemoNotice />
    {state.status === "ready" && <dl className="case-instrument-strip queue-summary" aria-label="Saved demo case summary">
      <div><dt>Saved reviews</dt><dd>{cases.length}</dd></div>
      <div><dt>Open</dt><dd>{openCount}</dd></div>
      <div><dt>Closed</dt><dd>{cases.length - openCount}</dd></div>
    </dl>}
    <section className="card">
      <div className="card-head">
        <div><p className="section-eyebrow">Recorded work</p><h2>Saved review records</h2><p className="card-subtitle">Synthetic cases stored by the connected demo API.</p></div>
        <div className="queue-filter"><label htmlFor="case-view">Show</label><select id="case-view" value={view} onChange={(event) => setView(event.target.value)} disabled={state.status !== "ready"}><option value="all">All records</option><option value="open">Open records</option><option value="closed">Closed records</option></select></div>
      </div>
      {state.status === "loading" && <div className="card-body" role="status">Loading saved review records…</div>}
      {state.status === "unavailable" && <div className="card-body" role="status"><p>Saved cases are unavailable. Reconnect to the demo API to see them.</p><button className="button secondary" onClick={retry}>Try again</button></div>}
      {state.status === "ready" && cases.length === 0 && <div className="card-body queue-state"><h3>Your first review starts with an observation.</h3><p className="detail-note">No review records have been saved yet.</p><Link className="button" href="/monitor/aberdare">Review a demo observation</Link></div>}
      {state.status === "ready" && cases.length > 0 && visibleCases.length === 0 && <div className="card-body queue-state"><p>No records match this view.</p><button className="button secondary" onClick={() => setView("all")}>Show all records</button></div>}
      {state.status === "ready" && visibleCases.length > 0 && <div className="table-scroll"><table className="source-table"><thead><tr><th scope="col">Case</th><th scope="col">Observation basis</th><th scope="col">Assigned owner</th><th scope="col">Status</th><th scope="col"><span className="sr-only">Open case</span></th></tr></thead><tbody>{visibleCases.map((item) => <tr key={item.id}>
        <td><span className="case-title">{item.title}</span><br /><span className="case-meta">{item.id} · opened {formatDate(item.openedAt)}</span></td>
        <td>{item.observationClassification.replaceAll("_", " ")}<br /><span className="case-meta instrument">{item.observationId}</span></td>
        <td>{item.owner}</td>
        <td><StatusChip status={item.status} /></td>
        <td><Link className="link-arrow" href={`/cases/${encodeURIComponent(item.id)}`}>Review →</Link></td>
      </tr>)}</tbody></table></div>}
    </section>
  </div>;
}
