import { DemoNotice } from "@/components/demo-notice";
import { CopernicusContext } from "@/components/copernicus-context";
import { demoMode } from "@/lib/demo";

const sources = [
  ["ForestProof demo provider", "Synthetic observation records", "Working in demo", "Deterministic fixtures support case workflow testing."],
  ["Sentinel-2 Level-2A", "Aggregate usable visibility", "Public report", "Published through the separate Geta research service. Coverage counts and source-check dates have distinct meanings."],
  ["NASA OPERA", "Historical observation and radar research", "Research", "Archived samples and bounded backtests require additional qualification for current alert monitoring."],
  ["GFW Tile Cache API", "Optional raster map context", "Disabled by default", "A bounded request and applicable terms require verification before enabling the map overlay."],
  ["GFW Data API", "Candidate record-level source", "Access unqualified", "Verify native eligibility, automated access, cost and publication rights for the chosen monitoring area."],
  ["Copernicus Data Space STAC", "Acquisition discovery", "Optional owner lookup", "A scene footprint establishes acquisition context. Local usable coverage needs a separate assessment."],
  ["NASA FIRMS", "Fire and thermal context", "Candidate", "A map key, source terms and suitability for the intended use require verification."],
];

export default function SourcesPage() {
  return <div className="page source-observatory">
    <div className="topline">
      <div><p className="eyebrow">Source observatory</p><h1>Know what each source can tell you.</h1><p className="lede">Keep source identity, acquisition dates, processing and coverage limits attached to every observation.</p></div>
      <span className="demo-chip">{demoMode.label}</span>
    </div>
    <DemoNotice />
    <aside className="source-public-report"><div><p className="section-eyebrow">Explore the public data</p><h2>What could Sentinel-2 assess over Geta?</h2><p>The public report compares usable optical coverage across dated passes and shows the latest successful source check.</p></div><a className="button" href="https://vmi3711898.contaboserver.net/visibility">Open visibility report ↗</a></aside>
    <section className="card">
      <div className="card-head"><div><p className="section-eyebrow">Source and method</p><h2>Initial source manifest</h2><p className="card-subtitle">Each status describes the implementation available for that source.</p></div></div>
      <div className="table-scroll"><table className="source-table"><thead><tr><th scope="col">Source</th><th scope="col">Use</th><th scope="col">Status</th><th scope="col">Interpretation</th></tr></thead><tbody>{sources.map(([name, use, status, constraint]) => <tr key={name}><td>{name}</td><td>{use}</td><td><span className="source-chip">{status}</span></td><td>{constraint}</td></tr>)}</tbody></table></div>
    </section>
    <CopernicusContext />
    <p className="detail-note source-footnote">Review provider terms and operating costs before enabling record-level alert ingestion.</p>
  </div>;
}
