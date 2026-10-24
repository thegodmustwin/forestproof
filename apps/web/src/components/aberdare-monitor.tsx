"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AberdareMap } from "@/components/aberdare-map";
import { DemoNotice } from "@/components/demo-notice";
import { ObservationDetail } from "@/components/observation-detail";
import { demoMode, DemoObservation, observations } from "@/lib/demo";
import { createCase, loadObservations } from "@/lib/api";

export function AberdareMonitor() {
  const [records, setRecords] = useState<DemoObservation[]>(observations);
  const [selected, setSelected] = useState<DemoObservation>(observations[0]);
  const [connection, setConnection] = useState("Loading API-backed observations; deterministic demo fixtures remain available if the API is offline.");
  const [created, setCreated] = useState<string | null>(null);
  const [createdCaseId, setCreatedCaseId] = useState<string | null>(null);
  const isDemo = records.every((item) => item.qualityFlags.includes("DEMO_DATA"));

  useEffect(() => {
    let active = true;
    void loadObservations()
      .then(({ items }) => {
        if (!active) return;
        setRecords(items);
        setSelected(items[0]);
        setConnection("API connected. The source provenance and quality flags shown with each record remain decisive for interpretation.");
      })
      .catch(() => {
        if (!active) return;
        setConnection("API unavailable. Showing deterministic, local demo fixtures only; no live source connection is implied.");
      });
    return () => { active = false; };
  }, []);

  const selectObservation = useCallback((item: DemoObservation) => {
    setSelected(item);
    setCreated(null);
    setCreatedCaseId(null);
  }, []);

  const submitCase = useCallback(async () => {
    setCreated("Creating a review record through the configured API…");
    setCreatedCaseId(null);
    try {
      const result = await createCase(selected);
      setCreatedCaseId(result.id ?? null);
      setCreated(result.id
        ? `Review record ${result.id} created through the API. It is a workflow record, not a finding of wrongdoing.`
        : "Review record created through the API. It is a workflow record, not a finding of wrongdoing.");
    } catch {
      setCreatedCaseId(null);
      setCreated("The API could not create a case. No server-side record was written; this screen remains in local demo mode.");
    }
  }, [selected]);

  return (
    <div className="page">
      <div className="topline"><div><p className="eyebrow">Monitor / Aberdare</p><h1>Observation is the start of the record.</h1><p className="lede">Review source timing, confidence, classification, and missing evidence before routing an investigation.</p></div><span className="demo-chip">{isDemo ? demoMode.label : "API RECORDS"}</span></div>
      {isDemo ? <DemoNotice /> : <aside className="notice" role="note"><span aria-hidden="true">⚑</span><span><b>API-BACKED RECORDS.</b> These records still require source-grounded, authorised human review. An observation does not establish legal status or wrongdoing.</span></aside>}
      <p className="detail-note" style={{ margin: "-11px 0 18px" }} aria-live="polite">{connection}</p>
      <div className="map-layout">
        <AberdareMap selectedId={selected.id} observations={records} onSelect={selectObservation} />
        <aside className="card detail-panel">
          <ObservationDetail observation={selected} onCreateCase={submitCase} />
          {created && <div className="notice" style={{ margin: "0 18px 18px" }}><span aria-hidden="true">✓</span><span>{created} {createdCaseId && <Link className="link-arrow" href={`/cases/${createdCaseId}`}>Open the review record →</Link>}</span></div>}
        </aside>
      </div>
      <section className="card section-gap"><div className="card-head"><div><h2>Interpretation guardrails</h2><p className="card-subtitle">The platform documents uncertainty rather than converting remote sensing into an allegation.</p></div></div><div className="card-body"><div className="two-column"><ul className="bullet-list"><li>Satellite or sensor observations can establish neither intent nor legal status on their own.</li><li>Observed, published, and ingested times remain distinct to avoid false real-time claims.</li></ul><ul className="bullet-list"><li>Land classification, permit evidence, and court context require authoritative sources and qualified review.</li><li>A priority score is a transparent triage aid, never an enforcement instruction.</li></ul></div></div></section>
    </div>
  );
}
