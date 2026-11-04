const nodes = [
  ["Observation", "Source provenance"],
  ["Review", "Human assessment"],
  ["Case", "Accountable owner"],
  ["Action", "Recorded response"],
  ["Follow-up", "Observed context"],
  ["Learning", "Outcome graph"],
];

function GraphIcon({ index }: { index: number }) {
  return <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    {index === 0 && <><circle cx="12" cy="12" r="6" /><path d="M12 2v4m0 12v4M2 12h4m12 0h4" /></>}
    {index === 1 && <path d="m5 12 4 4L19 6" />}
    {index === 2 && <><path d="M6 3h8l4 4v14H6V3Z" /><path d="M14 3v5h4M9 12h6m-6 4h6" /></>}
    {index === 3 && <><path d="M5 4v10h13m-4-4 4 4-4 4" /></>}
    {index === 4 && <><path d="M19 8a8 8 0 1 0 1 8M19 3v5h-5" /><path d="M12 8v5l3 2" /></>}
    {index === 5 && <><circle cx="5" cy="12" r="2" /><circle cx="19" cy="5" r="2" /><circle cx="19" cy="19" r="2" /><path d="M7 12h4l6-7m-6 7 6 7" /></>}
  </svg>;
}

export function OutcomeGraph() {
  return (
    <div className="outcome-graph" aria-label="Forest intervention outcome graph">
      {nodes.map(([label, caption], index) => (
        <div className="outcome-node" key={label}>
          <div className="outcome-node-icon" aria-hidden="true"><GraphIcon index={index} /></div>
          <div className="outcome-node-label">{label}</div>
          <div className="outcome-node-caption">{caption}</div>
        </div>
      ))}
    </div>
  );
}
