"use client";

import Link from "next/link";
import { DemoObservation, formatDate, toPriorityScore } from "@/lib/demo";

export function ObservationDetail({ observation, onCreateCase, creating = false }: { observation: DemoObservation; onCreateCase?: () => void | Promise<void>; creating?: boolean }) {
  return (
    <>
      <div className="card-head">
        <div>
          <div className="source-chip">{observation.status.replaceAll("_", " ")}</div>
          <h2 className="detail-title">{observation.title}</h2>
          <p className="detail-note">{observation.note}</p>
        </div>
      </div>
      <div className="card-body">
        <div className="facts">
          <div className="fact"><span className="fact-label">Record</span><b>{observation.id}</b></div>
          <div className="fact"><span className="fact-label">Observed</span><span>{formatDate(observation.observedAt)}</span></div>
          <div className="fact"><span className="fact-label">Published</span><span>{formatDate(observation.publishedAt)}</span></div>
          <div className="fact"><span className="fact-label">Ingested</span><span>{formatDate(observation.ingestedAt)}</span></div>
          <div className="fact"><span className="fact-label">Source</span><span>{observation.source}</span></div>
          <div className="fact"><span className="fact-label">Product</span><span>{observation.product}</span></div>
          <div className="fact"><span className="fact-label">Confidence</span><span>{observation.confidence}{observation.confidenceScore !== null ? ` · ${observation.confidenceScore}%` : ""}</span></div>
          <div className="fact"><span className="fact-label">Triage heuristic</span><span>{toPriorityScore(observation) === null ? "Not available" : `${toPriorityScore(observation)}/100 · not a decision`}</span></div>
          <div className="fact"><span className="fact-label">Quality flags</span><span className="flag-list">{observation.qualityFlags.map((flag) => <span className="flag" key={flag}>{flag}</span>)}</span></div>
        </div>
        <div className="button-row">
          <Link className="button secondary" href="/operations">View case queue</Link>
          {onCreateCase && <button className="button" disabled={creating} onClick={() => { void onCreateCase(); }}>{creating ? "Opening case…" : "Create review case"}</button>}
        </div>
      </div>
    </>
  );
}
