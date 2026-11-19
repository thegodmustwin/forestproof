import { DemoNotice } from "@/components/demo-notice";
import { demoMode } from "@/lib/demo";

export default function LegalContextPage() {
  return <div className="page legal-library">
    <div className="topline">
      <div><p className="eyebrow">Evidence paper / Legal context</p><h1>Keep the source in view.</h1><p className="lede">Review a document's authority, dates and geographic scope before applying it to an observation.</p></div>
      <span className="demo-chip">{demoMode.label}</span>
    </div>
    <DemoNotice />
    <section className="two-column">
      <article className="card">
        <div className="card-head"><div><p className="section-eyebrow">Document library</p><h2>Current demo registry</h2><p className="card-subtitle">No court order, permit, restriction, or legal conclusion is loaded into this demo.</p></div></div>
        <div className="card-body">
          <p className="library-count"><strong>0</strong> verified records</p>
          <div className="facts"><div className="fact"><span className="fact-label">Jurisdiction</span><span>Not configured</span></div><div className="fact"><span className="fact-label">Geographic scope</span><span>Not configured</span></div><div className="fact"><span className="fact-label">Verification owner</span><span>Not assigned</span></div></div>
        </div>
      </article>
      <article className="card">
        <div className="card-head"><div><p className="section-eyebrow">Review requirements</p><h2>Before a rule is displayed</h2></div></div>
        <div className="card-body"><ul className="document-requirements">
          <li><h3>Establish authority</h3><p>Retain an authoritative source or qualify the limits of a secondary source.</p></li>
          <li><h3>Identify the record</h3><p>Preserve the issuing body, document identifier and operative date.</p></li>
          <li><h3>Check applicability</h3><p>Record geographic scope, amendments, current status and limitations.</p></li>
          <li><h3>Assign review</h3><p>Keep a named qualified reviewer and a version history.</p></li>
        </ul></div>
      </article>
    </section>
    <section className="card section-gap"><div className="card-head"><div><h2>Human review carries the decision</h2></div></div><div className="card-body"><p className="detail-note">ForestProof can place a documented source alongside an observation so an authorized reviewer can evaluate its applicability and record missing evidence. Legal and enforcement decisions require the appropriate qualified people and institutions.</p></div></section>
  </div>;
}
