"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { DemoNotice } from "@/components/demo-notice";
import { StatusChip } from "@/components/status-chip";
import { WorkflowStrip } from "@/components/workflow-strip";
import { CaseStatus, caseStatusLabels, demoMode, formatDate, getCase, getObservation } from "@/lib/demo";
import { attachDemoEvidence, fetchDossier, loadCaseRecord, transitionCase } from "@/lib/api";

const order: CaseStatus[] = ["NEW", "UNDER_REVIEW", "FIELD_VERIFICATION", "ACTION_RECORDED", "FOLLOW_UP", "CLOSED"];

export function CaseWorkspace({ id }: { id: string }) {
  const [record, setRecord] = useState(() => getCase(id));
  const [observation, setObservation] = useState(() => getObservation(getCase(id).observationId));
  const [fromApi, setFromApi] = useState(false);
  const [recorded, setRecorded] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    setRecord(getCase(id));
    setObservation(getObservation(getCase(id).observationId));
    setFromApi(false);
    setRecorded(null);
    void loadCaseRecord(id).then((loaded) => {
      if (!active) return;
      setRecord(loaded.record);
      setObservation(loaded.observation);
      setFromApi(loaded.fromApi);
    }).catch(() => {
      // A static DEMO fixture remains usable when the API is not started.
    });
    return () => { active = false; };
  }, [id]);
  const currentIndex = order.indexOf(record.status);
  const next = currentIndex < 0
    ? "UNDER_REVIEW"
    : order[Math.min(currentIndex + 1, order.length - 1)];

  const advance = async () => {
    if (next === record.status) return;
    if (!fromApi) {
      setRecord({ ...record, status: next });
      setRecorded(`Demo transition recorded locally: ${caseStatusLabels[record.status]} → ${caseStatusLabels[next]}. A configured API records this transition, actor, timestamp, and reason in its audit trail.`);
      return;
    }
    setRecorded("Recording the review-state transition through the API…");
    try {
      await transitionCase(record.id, next);
      const refreshed = await loadCaseRecord(record.id);
      setRecord(refreshed.record);
      setObservation(refreshed.observation);
      setRecorded(`API transition recorded: ${caseStatusLabels[record.status]} → ${caseStatusLabels[next]}. No legal or enforcement conclusion was created.`);
    } catch {
      setRecorded("The API could not record this transition. No local status change was made.");
    }
  };

  const addEvidence = async () => {
    if (!fromApi) {
      setRecorded("Demo evidence packet added locally. A configured API calculates SHA-256, validates the payload, stores it privately, and appends an audit event.");
      return;
    }
    setRecorded("Attaching the labelled synthetic evidence packet through the API…");
    try {
      await attachDemoEvidence(record.id);
      const refreshed = await loadCaseRecord(record.id);
      setRecord(refreshed.record);
      setObservation(refreshed.observation);
      setRecorded("Synthetic evidence packet attached. Its hash will be re-checked when a dossier is generated.");
    } catch {
      setRecorded("The API could not attach evidence. No local evidence record was added.");
    }
  };

  const generateDossier = async () => {
    if (!fromApi) {
      setRecorded("A demo evidence dossier would now be generated. Production export includes identifiers, sources, timestamps, evidence hashes, and reviewer actions.");
      return;
    }
    try {
      const dossier = await fetchDossier(record.id);
      const blob = new Blob([JSON.stringify(dossier, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `forestproof-dossier-${record.id}.json`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      setRecorded("EvidenceProof JSON dossier downloaded. It reports hash verification and does not make a legal finding.");
    } catch {
      setRecorded("The API could not generate a dossier. No export was created.");
    }
  };

  return <div className="page"><div className="topline"><div><p className="eyebrow">Investigation case / {record.id}</p><h1>{record.title}</h1><p className="lede">A reviewable record with a source basis, an accountable owner, evidence history, and an explicit scope of uncertainty.</p></div><span className="demo-chip">{fromApi ? "API-BACKED DEMO" : demoMode.label}</span></div><DemoNotice />
    <section className="card"><div className="card-head"><div><div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}><h2>Case state</h2><StatusChip status={record.status} /></div><p className="card-subtitle">No status is a legal or enforcement finding.</p></div><div className="button-row"><button className="button secondary" onClick={addEvidence}>Add demo evidence</button><button className="button" disabled={next === record.status} onClick={advance}>Record {caseStatusLabels[next]}</button></div></div><div className="card-body"><WorkflowStrip current={record.status} /></div></section>
    {recorded && <div className="notice section-gap"><span aria-hidden="true">✓</span><span>{recorded}</span></div>}
    <section className="two-column section-gap"><article className="card"><div className="card-head"><div><h2>Evidence basis</h2><p className="card-subtitle">Every field preserves its provenance and limitation.</p></div></div><div className="card-body"><div className="facts"><div className="fact"><span className="fact-label">Source observation</span><span><Link className="link-arrow" href="/monitor/aberdare">{observation.id}</Link></span></div><div className="fact"><span className="fact-label">Classification</span><span>{observation.classification}</span></div><div className="fact"><span className="fact-label">Observed time</span><span>{formatDate(observation.observedAt)}</span></div><div className="fact"><span className="fact-label">Confidence</span><span>{observation.confidence}</span></div><div className="fact"><span className="fact-label">Evidence records</span><span>{record.evidenceCount} demo metadata entries</span></div><div className="fact"><span className="fact-label">Integrity status</span><span>Hashes are checked at dossier generation · not independent proof</span></div></div><p className="detail-note">{observation.note}</p></div></article><article className="card"><div className="card-head"><div><h2>Accountability</h2><p className="card-subtitle">Authority is recorded rather than assumed.</p></div></div><div className="card-body"><div className="facts"><div className="fact"><span className="fact-label">Owner</span><span>{record.owner}</span></div><div className="fact"><span className="fact-label">Triage</span><span>{record.priority} · transparent demo heuristic</span></div><div className="fact"><span className="fact-label">Legal context</span><span>None verified or loaded</span></div><div className="fact"><span className="fact-label">Permission state</span><span>Unknown · not inferred</span></div></div><div className="button-row"><button className="button secondary" onClick={generateDossier}>Generate demo dossier</button></div></div></article></section>
    <section className="card section-gap"><div className="card-head"><div><h2>Append-only review timeline</h2><p className="card-subtitle">History records what was actually entered, by whom, and when.</p></div></div><div className="card-body"><div className="timeline">{record.timeline.map((entry) => <div className="timeline-entry" key={`${entry.at}-${entry.label}`}><div className="timeline-time">{formatDate(entry.at)}</div><div className="timeline-label">{entry.label}</div><div className="timeline-detail">{entry.detail}</div><div className="timeline-actor">{entry.actor}</div></div>)}</div></div></section>
  </div>;
}
