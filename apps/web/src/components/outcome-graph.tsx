const nodes = [
  ["⌖", "Observation", "Source provenance"],
  ["✓", "Review", "Human assessment"],
  ["□", "Case", "Accountable owner"],
  ["↳", "Action", "Recorded response"],
  ["◌", "Follow-up", "Observed context"],
  ["⌁", "Learning", "Outcome graph"],
];

export function OutcomeGraph() {
  return (
    <div className="outcome-graph" aria-label="Forest intervention outcome graph">
      {nodes.map(([icon, label, caption]) => (
        <div className="outcome-node" key={label}>
          <div className="outcome-node-icon" aria-hidden="true">{icon}</div>
          <div className="outcome-node-label">{label}</div>
          <div className="outcome-node-caption">{caption}</div>
        </div>
      ))}
    </div>
  );
}
