import { CaseStatus, caseStatusLabels } from "@/lib/demo";

export function StatusChip({ status }: { status: CaseStatus | string }) {
  const tone = status === "UNDER_REVIEW" || status === "FIELD_VERIFICATION" ? "amber" : status === "REOPENED" ? "red" : "";
  const label = caseStatusLabels[status as CaseStatus] ?? status.replaceAll("_", " ");
  return <span className={`status-chip ${tone}`}>{label}</span>;
}
