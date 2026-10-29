"use client";

import { useState } from "react";
import { CopernicusSceneContext, loadCopernicusSceneContext } from "@/lib/api";
import { formatDate } from "@/lib/demo";

type LookupState = { status: "idle" | "loading" | "unavailable" } | { status: "ready"; data: CopernicusSceneContext };

export function CopernicusContext() {
  const [state, setState] = useState<LookupState>({ status: "idle" });
  async function lookup() {
    if (state.status === "loading") return;
    setState({ status: "loading" });
    try { setState({ status: "ready", data: await loadCopernicusSceneContext() }); }
    catch { setState({ status: "unavailable" }); }
  }

  return <section className="card section-gap">
    <div className="card-head"><div><h2>Recent satellite scene context</h2><p className="card-subtitle">An optional owner-only lookup from the Copernicus catalog.</p></div></div>
    <div className="card-body">
      <p className="detail-note">Find up to three recent Sentinel-2 acquisitions returned for the provisional Geta-area research rectangle. The rectangle is not the official forest boundary, and bounding-box overlap does not establish complete area coverage. A scene is not a forest-loss alert; scene-wide cloud cover does not describe cloud conditions at every location.</p>
      <p className="detail-note">The lookup is off in the shared demo and runs only when explicitly enabled in an isolated owner demo. It retrieves metadata, not imagery. Results may be reused for 15 minutes.</p>
      <button className="button secondary" disabled={state.status === "loading"} onClick={() => { void lookup(); }}>{state.status === "loading" ? "Checking catalog…" : "Look up recent scenes"}</button>
      {state.status === "unavailable" && <p className="detail-note" role="status">The owner-only scene lookup is disabled or temporarily unavailable. No live alert feed is active.</p>}
      {state.status === "ready" && <div role="status">
        <p className="detail-note">Catalog checked {formatDate(state.data.checkedAt)} · results may be incomplete.</p>
        {state.data.scenes.length === 0 ? <p>No scenes were returned in this sample. This does not establish forest conditions or coverage.</p>
          : <table className="source-table"><thead><tr><th>Acquisition</th><th>Satellite</th><th>Scene cloud cover</th></tr></thead><tbody>{state.data.scenes.map((scene) => <tr key={scene.id}><td>{formatDate(scene.acquiredAt)}<br /><span className="case-meta">{scene.id}</span><br /><span className="case-meta">Copernicus Sentinel data {new Date(scene.acquiredAt).getUTCFullYear()}</span></td><td>{scene.platform ?? "Not provided"}</td><td>{scene.sceneCloudCoverPercent === null ? "Not provided" : `${scene.sceneCloudCoverPercent}%`}</td></tr>)}</tbody></table>}
        <p className="detail-note">Source: Copernicus Data Space Ecosystem.</p>
      </div>}
    </div>
  </section>;
}
