export type ObservationStatus =
  | "REQUIRES_HUMAN_REVIEW"
  | "AUTHORIZATION_UNKNOWN"
  | "DOCUMENTED_AUTHORIZATION"
  | "INSUFFICIENT_EVIDENCE"
  | "FALSE_POSITIVE";

export type CaseStatus =
  | "NEW"
  | "UNDER_REVIEW"
  | "FIELD_VERIFICATION"
  | "ACTION_RECORDED"
  | "FOLLOW_UP"
  | "CLOSED"
  | "REOPENED";

export type DemoObservation = {
  id: string;
  title: string;
  source: string;
  product: string;
  sourceRecordId: string;
  observedAt: string;
  publishedAt: string;
  ingestedAt: string;
  coordinates: [number, number];
  confidence: string;
  confidenceScore: number | null;
  classification: string;
  status: ObservationStatus;
  forestClass: string;
  spatialResolution: string;
  qualityFlags: string[];
  note: string;
};

export type TimelineEntry = {
  at: string;
  label: string;
  detail: string;
  actor: string;
};

export type DemoCase = {
  id: string;
  title: string;
  status: CaseStatus;
  owner: string;
  priority: "High" | "Standard" | "Low";
  observationId: string;
  openedAt: string;
  evidenceCount: number;
  timeline: TimelineEntry[];
};

export const demoMode = {
  label: "DEMO MODE",
  description:
    "All case records and point observations below are deterministic synthetic fixtures. They are not live alerts, legal findings, boundaries, permits, or allegations.",
};

export const monitoredArea = {
  name: "Aberdare illustrative monitoring area",
  description:
    "A non-authoritative demonstration area used to test ForestProof workflows. It is not a legal forest boundary or a live operational assignment.",
  center: [36.74, -0.38] as [number, number],
  areaLabel: "Illustrative AOI · not an official boundary",
};

export const observations: DemoObservation[] = [
  {
    id: "DEMO-OBS-0042",
    title: "Vegetation-change review cue",
    source: "ForestProof deterministic demo provider",
    product: "Synthetic multi-observation fixture v1",
    sourceRecordId: "demo:aberdare:0042",
    observedAt: "2026-10-17T09:24:00Z",
    publishedAt: "2026-10-18T08:00:00Z",
    ingestedAt: "2026-10-18T08:03:11Z",
    coordinates: [36.723, -0.395],
    confidence: "Corroboration required",
    confidenceScore: 64,
    classification: "FOREST_DISTURBANCE_OBSERVED",
    status: "REQUIRES_HUMAN_REVIEW",
    forestClass: "Forest classification unavailable in demo",
    spatialResolution: "Demo fixture · no satellite resolution",
    qualityFlags: ["DEMO_DATA", "NOT_A_LIVE_DETECTION", "NO_LEGAL_DETERMINATION"],
    note:
      "A synthetic cue used to demonstrate review, evidence capture, and responsible triage. It does not establish harvesting, damage, or unlawful conduct.",
  },
  {
    id: "DEMO-OBS-0041",
    title: "Possible fire-context review cue",
    source: "ForestProof deterministic demo provider",
    product: "Synthetic thermal-context fixture v1",
    sourceRecordId: "demo:aberdare:0041",
    observedAt: "2026-10-16T13:00:00Z",
    publishedAt: "2026-10-16T16:21:00Z",
    ingestedAt: "2026-10-16T16:24:41Z",
    coordinates: [36.761, -0.37],
    confidence: "Context only",
    confidenceScore: 38,
    classification: "POSSIBLE_FIRE_DAMAGE",
    status: "INSUFFICIENT_EVIDENCE",
    forestClass: "Land classification unverified",
    spatialResolution: "Demo fixture · no satellite resolution",
    qualityFlags: ["DEMO_DATA", "FIRE_CONTEXT_ONLY", "REQUIRES_GROUND_REVIEW"],
    note:
      "This is a synthetic context signal. Thermal anomalies and forest disturbance are distinct observations and require qualified human interpretation.",
  },
  {
    id: "DEMO-OBS-0039",
    title: "Managed-activity verification cue",
    source: "ForestProof deterministic demo provider",
    product: "Synthetic authorization workflow fixture v1",
    sourceRecordId: "demo:aberdare:0039",
    observedAt: "2026-10-12T10:40:00Z",
    publishedAt: "2026-10-13T07:30:00Z",
    ingestedAt: "2026-10-13T07:33:08Z",
    coordinates: [36.704, -0.351],
    confidence: "Context review requested",
    confidenceScore: 51,
    classification: "PLANTATION_MANAGEMENT_POSSIBLE",
    status: "AUTHORIZATION_UNKNOWN",
    forestClass: "Classification must be established from authoritative data",
    spatialResolution: "Demo fixture · no satellite resolution",
    qualityFlags: ["DEMO_DATA", "NO_PERMIT_CONCLUSION", "HUMAN_REVIEW_REQUIRED"],
    note:
      "A demonstration of the workflow for distinguishing an observation from a decision about authorization or compliance.",
  },
];

export const cases: DemoCase[] = [
  {
    id: "DEMO-CASE-0017",
    title: "Review record for demo observation 0042",
    status: "UNDER_REVIEW",
    owner: "Demo conservation review team",
    priority: "High",
    observationId: "DEMO-OBS-0042",
    openedAt: "2026-10-18T09:10:00Z",
    evidenceCount: 3,
    timeline: [
      {
        at: "2026-10-18T09:10:00Z",
        label: "Case created",
        detail: "Created from a labelled demo observation. No conclusion about lawfulness or causation was made.",
        actor: "Demo workflow",
      },
      {
        at: "2026-10-18T09:14:00Z",
        label: "Assigned for review",
        detail: "Assignment is a workflow cue only; it does not represent an authorised field deployment.",
        actor: "Demo conservation review team",
      },
      {
        at: "2026-10-18T09:26:00Z",
        label: "Provenance checked",
        detail: "Fixture source, record identifier, and distinct time fields preserved in the audit trail.",
        actor: "Demo analyst",
      },
    ],
  },
  {
    id: "DEMO-CASE-0014",
    title: "Demo follow-up outcome record",
    status: "FOLLOW_UP",
    owner: "Demo watershed partner",
    priority: "Standard",
    observationId: "DEMO-OBS-0041",
    openedAt: "2026-10-16T17:02:00Z",
    evidenceCount: 2,
    timeline: [
      {
        at: "2026-10-16T17:02:00Z",
        label: "Case created",
        detail: "Synthetic case opened to exercise follow-up semantics.",
        actor: "Demo workflow",
      },
      {
        at: "2026-10-17T12:00:00Z",
        label: "Action recorded",
        detail: "The action is synthetic and is not evidence of a real intervention.",
        actor: "Demo reviewer",
      },
    ],
  },
];

export const caseStatusLabels: Record<CaseStatus, string> = {
  NEW: "New",
  UNDER_REVIEW: "Under review",
  FIELD_VERIFICATION: "Field verification",
  ACTION_RECORDED: "Action recorded",
  FOLLOW_UP: "Follow-up",
  CLOSED: "Closed",
  REOPENED: "Reopened",
};

export const getObservation = (id: string) => observations.find((item) => item.id === id) ?? observations[0];
/** A missing case or source observation must never resolve to another fixture. */
export function findDemoCase(id: string): { record: DemoCase; observation: DemoObservation } | null {
  const record = cases.find((item) => item.id === id);
  const observation = record && observations.find((item) => item.id === record.observationId);
  return record && observation ? { record, observation } : null;
}

export const formatDate = (value: string) =>
  Number.isNaN(Date.parse(value)) ? "Not provided" : new Intl.DateTimeFormat("en-KE", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  }).format(new Date(value)) + " UTC";

export const toPriorityScore = (observation: DemoObservation) =>
  observation.confidenceScore === null ? null : Math.round((observation.confidenceScore * 0.4 + 35) * 10) / 10;
