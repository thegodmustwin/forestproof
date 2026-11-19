"use client";

import Link from "next/link";
import { DemoObservation, formatDate, toPriorityScore } from "@/lib/demo";

export function ObservationDetail({ observation, onCreateCase, creating = false }: { observation: DemoObservation; onCreateCase?: () => void | Promise<void>; creating?: boolean }) {
  const priority = toPriorityScore(observation);
  return (
    <>
      <div className="card-head inspector-heading">
        <div>
          <p className="section-eyebrow">Evidence inspector</p>
          <div className="source-chip">{observation.status.replaceAll("_", " ")}</div>
          <h2 className="detail-title">{observation.title}</h2>
          <p className="detail-note">{observation.note}</p>
        </div>
      </div>
      <div className="card-body">
        <section aria-label="Observation summary">
          <div className="facts inspector-summary">
            <div className="fact"><span className="fact-label">Record</span><b className="instrument">{observation.id}</b></div>
            <div className="fact"><span className="fact-label">Observed</span><span>{formatDate(observation.observedAt)}</span></div>
            <div className="fact"><span className="fact-label">Source</span><span>{observation.source}</span></div>
            <div className="fact"><span className="fact-label">Confidence</span><span>{observation.confidence}{observation.confidenceScore !== null ? " · " + observation.confidenceScore + "%" : ""}</span></div>
          </div>
        </section>
        <section className="source-quality" aria-labelledby="source-quality-heading">
          <h3 id="source-quality-heading">Source quality</h3>
          <p className="detail-note">Read the quality flags before deciding what to review.</p>
          <div className="flag-list">{observation.qualityFlags.map((flag) => <span className="flag" key={flag}>{flag}</span>)}</div>
          <div className="facts">
            <div className="fact"><span className="fact-label">Coverage completeness</span><span>{observation.sourceProvenance ? "Unknown" : "Not provided"}</span></div>
            <div className="fact"><span className="fact-label">Triage heuristic</span><span>{priority === null ? "Not available" : priority + "/100 · review aid"}</span></div>
          </div>
        </section>
        <details className="provenance-details">
          <summary>Source record and processing</summary>
          <div className="facts">
            <div className="fact"><span className="fact-label">Product</span><span>{observation.product}</span></div>
            <div className="fact"><span className="fact-label">Source record</span><span className="instrument">{observation.sourceRecordId}</span></div>
            <div className="fact"><span className="fact-label">Published</span><span>{formatDate(observation.publishedAt)}</span></div>
            <div className="fact"><span className="fact-label">Ingested</span><span>{formatDate(observation.ingestedAt)}</span></div>
            <div className="fact"><span className="fact-label">Processing version</span><span>{observation.sourceProvenance?.processingVersion ?? "Not provided"}</span></div>
            <div className="fact"><span className="fact-label">Source release</span><span>{observation.sourceProvenance?.sourceRelease ?? "Not provided"}</span></div>
            <div className="fact"><span className="fact-label">Attribution</span><span>{observation.sourceProvenance?.attribution ?? "Not provided"}</span></div>
          </div>
        </details>
        <div className="inspector-action">
          <p className="section-eyebrow">Next step</p>
          <div className="button-row">
            {onCreateCase && <button className="button" disabled={creating} onClick={() => { void onCreateCase(); }}>{creating ? "Opening case…" : "Create review case"}</button>}
            <Link className="button secondary" href="/operations">View case queue</Link>
          </div>
        </div>
      </div>
    </>
  );
}
