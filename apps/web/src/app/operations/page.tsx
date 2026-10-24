import Link from "next/link";
import { DemoNotice } from "@/components/demo-notice";
import { StatusChip } from "@/components/status-chip";
import { cases, demoMode, formatDate, getObservation } from "@/lib/demo";

export default function OperationsPage() {
  return <div className="page"><div className="topline"><div><p className="eyebrow">Operations / Case queue</p><h1>Route evidence, not accusations.</h1><p className="lede">An accountable workflow assigns review to authorised people and preserves the decisions they actually make.</p></div><span className="demo-chip">{demoMode.label}</span></div><DemoNotice /><section className="card"><div className="card-head"><div><h2>Open records</h2><p className="card-subtitle">Case data is synthetic in this preview.</p></div><span className="source-chip">{cases.length} records</span></div><div className="card-body" style={{ padding: 0 }}><table className="source-table"><thead><tr><th>Case</th><th>Observation basis</th><th>Assigned owner</th><th>Status</th><th></th></tr></thead><tbody>{cases.map((item) => { const observation = getObservation(item.observationId); return <tr key={item.id}><td>{item.title}<br /><span className="case-meta">{item.id} · opened {formatDate(item.openedAt)}</span></td><td>{observation.classification}<br /><span className="case-meta">{observation.confidence}</span></td><td>{item.owner}</td><td><StatusChip status={item.status} /></td><td><Link className="link-arrow" href={`/cases/${item.id}`}>Review →</Link></td></tr>; })}</tbody></table></div></section></div>;
}
