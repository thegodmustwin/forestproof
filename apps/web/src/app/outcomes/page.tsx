import { DemoNotice } from "@/components/demo-notice";
import { OutcomeGraph } from "@/components/outcome-graph";
import { demoMode } from "@/lib/demo";

export default function OutcomesPage() {
  return <div className="page">
    <div className="topline"><div><p className="eyebrow">Outcome intelligence</p><h1>Follow the evidence.</h1><p className="lede">Choose one saved case and retrace its observation, reviewer response, and follow-up. Every connection comes from its recorded workflow.</p></div><span className="demo-chip">{demoMode.label}</span></div>
    <DemoNotice />
    <section className="card"><div className="card-body"><OutcomeGraph /></div></section>
  </div>;
}
