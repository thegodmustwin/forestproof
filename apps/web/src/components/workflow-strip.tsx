import { CaseStatus, caseStatusLabels } from "@/lib/demo";

const steps: CaseStatus[] = ["NEW", "UNDER_REVIEW", "FIELD_VERIFICATION", "ACTION_RECORDED", "FOLLOW_UP", "CLOSED"];

export function WorkflowStrip({ current }: { current: CaseStatus }) {
  const currentIndex = steps.indexOf(current);
  return (
    <div className="workflow" aria-label={`Current case workflow state: ${caseStatusLabels[current]}`}>
      {steps.map((step, index) => (
        <div className={`workflow-step ${index <= currentIndex ? "active" : "pending"}`} key={step}>
          <span className="workflow-dot">{index + 1}</span>
          <div className="workflow-name">{caseStatusLabels[step]}</div>
          <div className="workflow-detail">{current === "REOPENED" ? "See retained history" : index === currentIndex ? "Current state" : index < currentIndex ? "Recorded" : "Not yet recorded"}</div>
        </div>
      ))}
    </div>
  );
}
