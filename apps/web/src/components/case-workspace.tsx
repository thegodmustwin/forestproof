"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { DemoNotice } from "@/components/demo-notice";
import { StatusChip } from "@/components/status-chip";
import { WorkflowStrip } from "@/components/workflow-strip";
import { CaseStatus, DemoCase, DemoObservation, caseStatusLabels, demoMode, findDemoCase, formatDate } from "@/lib/demo";
import { CaseAction, CaseFollowUp, FollowUpAssessment, LoadedCase, attachDemoEvidence, fetchDossier, loadCaseRecord, recordDemoAction, recordDemoFollowUp, transitionCase } from "@/lib/api";

const nextStatus: Record<CaseStatus, CaseStatus> = {
  NEW: "UNDER_REVIEW", UNDER_REVIEW: "FIELD_VERIFICATION", FIELD_VERIFICATION: "ACTION_RECORDED",
  ACTION_RECORDED: "FOLLOW_UP", FOLLOW_UP: "CLOSED", CLOSED: "REOPENED", REOPENED: "UNDER_REVIEW",
};

export function CaseWorkspace({ id }: { id: string }) {
  const [record, setRecord] = useState<DemoCase | null>(null);
  const [observation, setObservation] = useState<DemoObservation | null>(null);
  const [actions, setActions] = useState<CaseAction[]>([]);
  const [followUps, setFollowUps] = useState<CaseFollowUp[]>([]);
  const [fromApi, setFromApi] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [recorded, setRecorded] = useState<string | null>(null);
  const [actionText, setActionText] = useState("");
  const [followUpText, setFollowUpText] = useState("");
  const [assessment, setAssessment] = useState<FollowUpAssessment>("UNRESOLVED");

  function applyLoaded(loaded: LoadedCase) {
    setRecord(loaded.record);
    setObservation(loaded.observation);
    setActions(loaded.actions);
    setFollowUps(loaded.followUps);
    setFromApi(loaded.fromApi);
  }

  useEffect(() => {
    let active = true;
    setRecord(null);
    setObservation(null);
    setActions([]);
    setFollowUps([]);
    setFromApi(false);
    setLoading(true);
    setRecorded(null);
    setActionText("");
    setFollowUpText("");
    void loadCaseRecord(id).then((loaded) => {
      if (!active) return;
      applyLoaded(loaded);
      setLoading(false);
    }).catch(() => {
      if (!active) return;
      const fixture = findDemoCase(id);
      if (fixture) {
        setRecord(fixture.record);
        setObservation(fixture.observation);
      }
      setLoading(false);
    });
    return () => { active = false; };
  }, [id]);

  if (loading || (record && record.id !== id)) return <div className="page"><p role="status">Loading case…</p></div>;
  if (!record || !observation) return <div className="page"><div className="topline"><div><p className="eyebrow">Investigation case</p><h1>Case unavailable</h1><p className="lede">This case could not be found or the API is unavailable. No other case has been substituted.</p><Link className="link-arrow" href="/operations">Return to the case queue →</Link></div></div></div>;

  const next = nextStatus[record.status];
  const needsAction = record.status === "FIELD_VERIFICATION" && actions.length === 0;
  const needsFollowUp = record.status === "FOLLOW_UP" && followUps.length === 0;
  const advanceDisabled = !fromApi || busy || needsAction || needsFollowUp;

  async function refresh() { applyLoaded(await loadCaseRecord(id)); }

  async function advance() {
    if (advanceDisabled || !record) return;
    const previous = record.status;
    setBusy(true);
    setRecorded("Saving the demo workflow transition…");
    try {
      await transitionCase(id, next);
      await refresh();
      setRecorded(`Saved: ${caseStatusLabels[previous]} → ${caseStatusLabels[next]}.`);
    } catch {
      setRecorded("The API could not confirm the transition. Reload the case to check its saved state before trying again.");
    } finally { setBusy(false); }
  }

  async function addAction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!fromApi || busy || actionText.trim().length < 2) return;
    setBusy(true);
    setRecorded("Saving the synthetic action…");
    try {
      await recordDemoAction(id, actionText.trim());
      await refresh();
      setActionText("");
      setRecorded("Synthetic action saved. You can now advance the case.");
    } catch {
      setRecorded("The API could not confirm the action. Reload the case and check its records before retrying.");
    } finally { setBusy(false); }
  }

  async function addFollowUp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!fromApi || busy || followUpText.trim().length < 2) return;
    setBusy(true);
    setRecorded("Saving the synthetic follow-up…");
    try {
      await recordDemoFollowUp(id, assessment, followUpText.trim());
      await refresh();
      setFollowUpText("");
      setRecorded("Synthetic follow-up saved. You can now close the case.");
    } catch {
      setRecorded("The API could not confirm the follow-up. Reload the case and check its records before retrying.");
    } finally { setBusy(false); }
  }

  async function addEvidence() {
    if (!fromApi || busy) return;
    setBusy(true);
    setRecorded("Attaching the labelled synthetic evidence packet…");
    try {
      await attachDemoEvidence(id);
      await refresh();
      setRecorded("Synthetic evidence packet attached. Its hash will be re-checked when a dossier is generated.");
    } catch {
      setRecorded("The API could not confirm the attachment. Uploads may be disabled in this preview; reload the case before retrying.");
    } finally { setBusy(false); }
  }

  async function generateDossier() {
    if (!fromApi || busy) return;
    setBusy(true);
    try {
      const dossier = await fetchDossier(id);
      const blob = new Blob([JSON.stringify(dossier, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `forestproof-dossier-${id}.json`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      setRecorded("Synthetic JSON dossier downloaded. It reports hash verification and does not make a legal finding.");
    } catch { setRecorded("The API could not generate a dossier. No export was created."); }
    finally { setBusy(false); }
  }

  return <div className="page">
    <div className="topline"><div><p className="eyebrow">Investigation case / {record.id}</p><h1>{record.title}</h1><p className="lede">A reviewable record with a source basis, an accountable owner, evidence history, and an explicit scope of uncertainty.</p></div><span className="demo-chip">{fromApi ? "API-BACKED DEMO" : demoMode.label}</span></div>
    <DemoNotice />
    {!fromApi && <div className="notice"><span aria-hidden="true">⚑</span><span>This is a local example. Connect to the demo API and create a saved case to record changes.</span></div>}
    <section className="card"><div className="card-head"><div><div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}><h2>Case state</h2><StatusChip status={record.status} /></div><p className="card-subtitle">No status is a legal or enforcement finding. Demo evidence attachments may be disabled in this preview.</p></div><div className="button-row"><button className="button secondary" disabled={!fromApi || busy} onClick={addEvidence}>Add demo evidence</button><button className="button" disabled={advanceDisabled} onClick={advance}>Advance to {caseStatusLabels[next]}</button></div></div><div className="card-body"><WorkflowStrip current={record.status} />{needsAction && fromApi && <p className="detail-note">Record a synthetic action below before advancing.</p>}{needsFollowUp && fromApi && <p className="detail-note">Record a synthetic follow-up below before closing.</p>}</div></section>
    {recorded && <div className="notice section-gap" role="status"><span aria-hidden="true">⚑</span><span>{recorded}</span></div>}
    {fromApi && record.status === "FIELD_VERIFICATION" && <section className="card section-gap"><div className="card-head"><div><h2>Record a demo action</h2><p className="card-subtitle">Use synthetic examples only; never enter real or personal information.</p></div></div><div className="card-body"><form className="review-form" onSubmit={(event) => { void addAction(event); }}><label htmlFor="demo-action">What action was taken?</label><textarea id="demo-action" value={actionText} onChange={(event) => setActionText(event.target.value)} maxLength={2000} placeholder="Describe a fictional review action" /><button className="button" disabled={busy || actionText.trim().length < 2}>Save demo action</button></form></div></section>}
    {fromApi && record.status === "FOLLOW_UP" && <section className="card section-gap"><div className="card-head"><div><h2>Record a demo follow-up</h2><p className="card-subtitle">The assessment is a synthetic workflow example, not a real-world finding.</p></div></div><div className="card-body"><form className="review-form" onSubmit={(event) => { void addFollowUp(event); }}><label htmlFor="demo-assessment">Assessment</label><select id="demo-assessment" value={assessment} onChange={(event) => setAssessment(event.target.value as FollowUpAssessment)}><option value="UNRESOLVED">Unresolved</option><option value="INSUFFICIENT_EVIDENCE">Insufficient evidence</option><option value="FALSE_POSITIVE">False positive</option><option value="VERIFIED_INCIDENT">Verified incident (synthetic)</option></select><label htmlFor="demo-follow-up">What did the follow-up find?</label><textarea id="demo-follow-up" value={followUpText} onChange={(event) => setFollowUpText(event.target.value)} maxLength={2000} placeholder="Describe a fictional follow-up" /><button className="button" disabled={busy || followUpText.trim().length < 2}>Save demo follow-up</button></form></div></section>}
    <section className="two-column section-gap"><article className="card"><div className="card-head"><div><h2>Evidence basis</h2><p className="card-subtitle">Every field preserves its provenance and limitation.</p></div></div><div className="card-body"><div className="facts"><div className="fact"><span className="fact-label">Source observation</span><span><Link className="link-arrow" href={`/monitor/aberdare?observation=${encodeURIComponent(observation.id)}`}>{observation.id}</Link></span></div><div className="fact"><span className="fact-label">Classification</span><span>{observation.classification}</span></div><div className="fact"><span className="fact-label">Observed time</span><span>{formatDate(observation.observedAt)}</span></div><div className="fact"><span className="fact-label">Confidence</span><span>{observation.confidence}</span></div><div className="fact"><span className="fact-label">Evidence records</span><span>{record.evidenceCount} demo metadata entries</span></div><div className="fact"><span className="fact-label">Integrity status</span><span>Hashes are checked at dossier generation · not independent proof</span></div></div><p className="detail-note">{observation.note}</p></div></article><article className="card"><div className="card-head"><div><h2>Accountability</h2><p className="card-subtitle">Authority is recorded rather than assumed.</p></div></div><div className="card-body"><div className="facts"><div className="fact"><span className="fact-label">Owner</span><span>{record.owner}</span></div><div className="fact"><span className="fact-label">Triage</span><span>{fromApi ? "Not recorded" : `${record.priority} · demo fixture`}</span></div><div className="fact"><span className="fact-label">Legal context</span><span>None verified or loaded</span></div><div className="fact"><span className="fact-label">Permission state</span><span>Unknown · not inferred</span></div></div><div className="button-row"><button className="button secondary" disabled={!fromApi || busy} onClick={generateDossier}>Generate demo dossier</button></div></div></article></section>
    {fromApi && (actions.length > 0 || followUps.length > 0) && <section className="card section-gap"><div className="card-head"><div><h2>Recorded demo actions and follow-ups</h2><p className="card-subtitle">Saved synthetic entries, not evidence of real interventions.</p></div></div><div className="card-body"><div className="timeline">{actions.map((item) => <div className="timeline-entry" key={`action-${item.id}`}><div className="timeline-time">{formatDate(item.occurredAt)}</div><div className="timeline-label">Action · {item.actionType.replaceAll("_", " ")}</div><div className="timeline-detail">{item.summary}</div><div className="timeline-actor">{item.recordedBy}</div></div>)}{followUps.map((item) => <div className="timeline-entry" key={`follow-up-${item.id}`}><div className="timeline-time">{formatDate(item.observedAt)}</div><div className="timeline-label">Follow-up · {item.assessment.replaceAll("_", " ")}</div><div className="timeline-detail">{item.summary}</div><div className="timeline-actor">{item.recordedBy}</div></div>)}</div></div></section>}
    <section className="card section-gap"><div className="card-head"><div><h2>Append-only review timeline</h2><p className="card-subtitle">History records what was actually entered, by whom, and when.</p></div></div><div className="card-body"><div className="timeline">{record.timeline.map((entry) => <div className="timeline-entry" key={`${entry.at}-${entry.label}`}><div className="timeline-time">{formatDate(entry.at)}</div><div className="timeline-label">{entry.label}</div><div className="timeline-detail">{entry.detail}</div><div className="timeline-actor">{entry.actor}</div></div>)}</div></div></section>
  </div>;
}
