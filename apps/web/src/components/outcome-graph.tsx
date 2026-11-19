"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { CaseSummary, LoadedCase, loadCaseQueue, loadCaseRecord } from "@/lib/api";
import { caseStatusLabels, formatDate } from "@/lib/demo";

export function CaseLineage({ caseData }: { caseData: LoadedCase }) {
  const { record, observation, actions, followUps, fromApi } = caseData;
  return (
    <section className="atlas-lineage" aria-labelledby="lineage-heading">
      <div className="atlas-lineage-heading">
        <div><p className="eyebrow">Evidence lineage</p><h2 id="lineage-heading">Retrace this case</h2></div>
        <span className="demo-chip">{fromApi ? "Saved DEMO records" : "Local DEMO example"}</span>
      </div>
      <p className="card-subtitle">Follow the source observation through the records entered by its reviewers.</p>
      <ol className="atlas-lineage-stages">
        <li>
          <span className="atlas-lineage-dot" aria-hidden="true" />
          <div><p className="eyebrow">Observation</p><h3>{observation.title}</h3>
            <p>{formatDate(observation.observedAt)} · {observation.source}</p>
            <Link className="link-arrow" href={"/monitor/aberdare?observation=" + encodeURIComponent(observation.id)}>Review source {observation.id} →</Link>
          </div>
        </li>
        <li>
          <span className="atlas-lineage-dot" aria-hidden="true" />
          <div><p className="eyebrow">Case</p><h3>{record.title}</h3>
            <p>{record.owner} · {caseStatusLabels[record.status]}</p>
            <Link className="link-arrow" href={"/cases/" + encodeURIComponent(record.id)}>Open case {record.id} →</Link>
          </div>
        </li>
        <li>
          <span className="atlas-lineage-dot" aria-hidden="true" />
          <div><p className="eyebrow">Evidence</p><h3>{record.evidenceCount} attachment {record.evidenceCount === 1 ? "record" : "records"}</h3>
            <p>{record.evidenceCount ? "Attachment records and their recorded hashes are included in the case dossier." : "No evidence attachments have been recorded."}</p>
          </div>
        </li>
        <li>
          <span className="atlas-lineage-dot" aria-hidden="true" />
          <div><p className="eyebrow">Response</p><h3>{actions.length} recorded {actions.length === 1 ? "action" : "actions"}</h3>
            {actions.length > 0 ? <ul>{actions.map((action) => <li key={action.id}><strong>{action.summary}</strong><p>{formatDate(action.occurredAt)} · {action.recordedBy}</p></li>)}</ul>
              : <p>{fromApi ? "A reviewer has yet to record an action." : "Connect this example to a saved case to inspect action records."}</p>}
          </div>
        </li>
        <li>
          <span className="atlas-lineage-dot" aria-hidden="true" />
          <div><p className="eyebrow">Follow-up</p><h3>{followUps.length} recorded {followUps.length === 1 ? "assessment" : "assessments"}</h3>
            {followUps.length > 0 ? <ul>{followUps.map((followUp) => <li key={followUp.id}><strong>{followUp.assessment.replaceAll("_", " ")}</strong><p>{followUp.summary}</p><p>{formatDate(followUp.observedAt)} · {followUp.recordedBy}</p></li>)}</ul>
              : <p>{fromApi ? "A follow-up assessment has yet to be recorded." : "Follow-up records are available for saved cases."}</p>}
          </div>
        </li>
      </ol>
      <p className="detail-note">These connections describe recorded workflow. Environmental outcomes require separate evidence.</p>
    </section>
  );
}

export function OutcomeGraph() {
  const [queue, setQueue] = useState<CaseSummary[] | null>(null);
  const [selectedId, setSelectedId] = useState("");
  const [caseData, setCaseData] = useState<LoadedCase | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    setCaseData(null);
    void loadCaseQueue().then((items) => {
      if (!active) return;
      setQueue(items);
      setSelectedId((id) => items.some((item) => item.id === id) ? id : items[0]?.id ?? "");
      if (items.length === 0) setLoading(false);
    }).catch(() => {
      if (!active) return;
      setError("Saved case records are unavailable. Try again when the demo API is connected.");
      setQueue(null);
      setCaseData(null);
      setLoading(false);
    });
    return () => { active = false; };
  }, [retry]);

  useEffect(() => {
    if (!selectedId) return;
    let active = true;
    setLoading(true);
    setError("");
    setCaseData(null);
    void loadCaseRecord(selectedId).then((record) => {
      if (!active) return;
      setCaseData(record);
      setLoading(false);
    }).catch(() => {
      if (!active) return;
      setError("This case could not be loaded. Select another saved case or try again.");
      setLoading(false);
    });
    return () => { active = false; };
  }, [selectedId, retry]);

  return <div className="atlas-outcomes">
    {queue && queue.length > 0 && <div className="atlas-lineage-picker">
      <label htmlFor="lineage-case">Choose a saved case</label>
      <select id="lineage-case" value={selectedId} onChange={(event) => setSelectedId(event.target.value)}>
        {queue.map((record) => <option key={record.id} value={record.id}>{record.title} · {record.id}</option>)}
      </select>
    </div>}
    {error && <div className="card-body" role="status"><p>{error}</p><button className="button secondary" type="button" onClick={() => setRetry((value) => value + 1)}>Try again</button></div>}
    {loading && <p className="card-body" role="status">Loading saved evidence relationships…</p>}
    {!loading && !error && queue?.length === 0 && <div className="card-body"><h2>Start with one case</h2><p>Save a review case from an observation to inspect its evidence and follow-up here.</p><Link className="button" href="/monitor/aberdare">Review a demo observation</Link></div>}
    {!loading && !error && caseData && <CaseLineage caseData={caseData} />}
  </div>;
}
