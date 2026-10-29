import { DemoNotice } from "@/components/demo-notice";
import { CopernicusContext } from "@/components/copernicus-context";
import { demoMode } from "@/lib/demo";

const sources = [
  ["ForestProof demo provider", "Deterministic fixture records", "Working in demo", "Synthetic only; never presented as an external environmental observation."],
  ["GFW Tile Cache API", "Raster context overlay", "Documented, not configured", "Raster pixels are map context, not individual case records or proof of illegality. Enable only after a bounded AOI request is verified."],
  ["GFW Data API", "Machine-readable alerts / datasets", "Available with credentials", "Server-side credential required; preserve queried version and original source metadata."],
  ["Copernicus Data Space STAC", "Acquisition discovery", "Optional owner lookup", "Satellite scenes are not forest-disturbance alerts; imagery downloads may require a token."],
  ["NASA FIRMS", "Fire and thermal context", "Requires map key", "Fire context only, not a general logging detector; resolution and latency must stay visible."],
];

export default function SourcesPage() {
  return <div className="page"><div className="topline"><div><p className="eyebrow">Source catalogue</p><h1>Provenance is a product feature.</h1><p className="lede">Every observation must retain where it came from, what version was used, when it was acquired, published, and ingested, plus the limits of its interpretation.</p></div><span className="demo-chip">{demoMode.label}</span></div><DemoNotice /><section className="card"><div className="card-head"><div><h2>Initial source manifest</h2><p className="card-subtitle">Operational status is intentionally conservative; “documented” does not mean a production feed is enabled.</p></div></div><div className="card-body" style={{ padding: "19px 9px" }}><table className="source-table"><thead><tr><th>Source</th><th>Proposed use</th><th>Status</th><th>Constraint</th></tr></thead><tbody>{sources.map(([name, use, status, constraint]) => <tr key={name}><td>{name}</td><td>{use}</td><td><span className="source-chip">{status}</span></td><td>{constraint}</td></tr>)}</tbody></table></div></section><CopernicusContext /><p className="detail-note" style={{ marginTop: 14 }}>Provider terms and operating costs must be reviewed before any live alert ingestion is enabled.</p></div>;
}
