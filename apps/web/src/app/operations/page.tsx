"use client";

import Link from "next/link";
import { DemoNotice } from "@/components/demo-notice";
import { StatusChip } from "@/components/status-chip";
import { demoMode, formatDate } from "@/lib/demo";
import { useCaseQueue } from "@/lib/use-case-queue";

export default function OperationsPage() {
  const { state, retry } = useCaseQueue();
  return <div className="page">
    <div className="topline"><div><p className="eyebrow">Operations / Case queue</p><h1>Route evidence, not accusations.</h1><p className="lede">An accountable workflow assigns review to authorised people and preserves the decisions they actually make.</p></div><span className="demo-chip">{demoMode.label}</span></div>
    <DemoNotice />
    <section className="card">
      <div className="card-head"><div><h2>Saved review records</h2><p className="card-subtitle">Synthetic cases stored by the connected demo API.</p></div>{state.status === "ready" && <span className="source-chip">{state.cases.length} {state.cases.length === 1 ? "record" : "records"}</span>}</div>
      {state.status === "loading" && <div className="card-body" role="status">Loading saved review records…</div>}
      {state.status === "unavailable" && <div className="card-body" role="status"><p>Saved cases are unavailable. Reconnect to the demo API to see them.</p><button className="button secondary" onClick={retry}>Try again</button></div>}
      {state.status === "ready" && state.cases.length === 0 && <div className="card-body"><p>No review records have been saved yet.</p><Link className="button" href="/monitor/aberdare">Review a demo observation</Link></div>}
      {state.status === "ready" && state.cases.length > 0 && <div className="card-body" style={{ padding: 0 }}><table className="source-table"><thead><tr><th>Case</th><th>Observation basis</th><th>Assigned owner</th><th>Status</th><th></th></tr></thead><tbody>{state.cases.map((item) => <tr key={item.id}><td>{item.title}<br /><span className="case-meta">{item.id} · opened {formatDate(item.openedAt)}</span></td><td>{item.observationClassification.replaceAll("_", " ")}<br /><span className="case-meta">{item.observationId}</span></td><td>{item.owner}</td><td><StatusChip status={item.status} /></td><td><Link className="link-arrow" href={`/cases/${encodeURIComponent(item.id)}`}>Review →</Link></td></tr>)}</tbody></table></div>}
    </section>
  </div>;
}
