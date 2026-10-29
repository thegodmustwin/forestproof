import { CaseStatus, DemoCase, DemoObservation, TimelineEntry } from "@/lib/demo";
import { normalizeDemoObservation } from "@/lib/observation-normalization";

// Local development may call the API directly. Hosted deployments deliberately
// use the same-origin proxy so the mutable demo API is not exposed publicly.
const localFallback = process.env.NODE_ENV === "development"
  ? "http://localhost:8000/api/v1"
  : "/api/forestproof";
const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? localFallback).replace(/\/$/, "");

type UnknownRecord = Record<string, unknown>;

function stringValue(value: unknown, fallback: string): string {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function caseStatusFrom(value: unknown): CaseStatus {
  const states: CaseStatus[] = ["NEW", "UNDER_REVIEW", "FIELD_VERIFICATION", "ACTION_RECORDED", "FOLLOW_UP", "CLOSED", "REOPENED"];
  if (typeof value !== "string" || !states.includes(value as CaseStatus)) throw new Error("Case response contained an unknown status");
  return value as CaseStatus;
}

function requiredString(value: unknown, field: string): string {
  if (typeof value !== "string" || !value.trim()) throw new Error(`Case response omitted ${field}`);
  return value;
}

export type CaseSummary = {
  id: string;
  title: string;
  status: CaseStatus;
  owner: string;
  observationId: string;
  observationClassification: string;
  openedAt: string;
};

export async function loadCaseQueue(): Promise<CaseSummary[]> {
  const response = await fetch(`${apiBase}/cases`, { headers: { Accept: "application/json" }, cache: "no-store" });
  if (!response.ok) throw new Error(`Case queue request failed (${response.status})`);
  const payload: unknown = await response.json();
  if (!payload || typeof payload !== "object" || !Array.isArray((payload as UnknownRecord).items)) {
    throw new Error("Case queue response was malformed");
  }
  return ((payload as UnknownRecord).items as unknown[]).map((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) throw new Error("Case queue contained an invalid record");
    const raw = item as UnknownRecord;
    if (!Array.isArray(raw.quality_flags) || !raw.quality_flags.includes("DEMO_DATA")) {
      throw new Error("Only explicitly labelled demo cases are supported");
    }
    return {
      id: requiredString(raw.id, "case ID"),
      title: requiredString(raw.title, "case title"),
      status: caseStatusFrom(raw.status),
      owner: stringValue(raw.owner_organization, "Unassigned"),
      observationId: requiredString(raw.observation_id, "observation ID"),
      observationClassification: stringValue(raw.observation_classification, "Classification unavailable"),
      openedAt: stringValue(raw.created_at, ""),
    };
  });
}

export type CopernicusScene = { id: string; acquiredAt: string; platform: string | null; sceneCloudCoverPercent: number | null };
export type CopernicusSceneContext = { checkedAt: string; scenes: CopernicusScene[] };

export async function loadCopernicusSceneContext(): Promise<CopernicusSceneContext> {
  const response = await fetch(`${apiBase}/context/copernicus-scenes`, { headers: { Accept: "application/json" }, cache: "no-store" });
  if (!response.ok) throw new Error("Satellite scene lookup is unavailable");
  const payload: unknown = await response.json();
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) throw new Error("Satellite scene response was malformed");
  const raw = payload as UnknownRecord;
  if (raw.collection !== "sentinel-2-l2a" || !Array.isArray(raw.scenes) || raw.scenes.length > 3) throw new Error("Satellite scene response was malformed");
  const checkedAt = requiredString(raw.checked_at, "catalog check time");
  if (Number.isNaN(Date.parse(checkedAt))) throw new Error("Satellite catalog check time was malformed");
  const scenes = raw.scenes.map((item: unknown): CopernicusScene => {
    if (!item || typeof item !== "object" || Array.isArray(item)) throw new Error("Satellite scene was malformed");
    const scene = item as UnknownRecord;
    const cloud = scene.scene_cloud_cover_percent;
    if (cloud !== null && (typeof cloud !== "number" || !Number.isFinite(cloud) || cloud < 0 || cloud > 100)) throw new Error("Satellite scene cloud cover was malformed");
    if (scene.platform !== null && typeof scene.platform !== "string") throw new Error("Satellite scene platform was malformed");
    const acquiredAt = requiredString(scene.acquired_at, "scene date");
    if (Number.isNaN(Date.parse(acquiredAt))) throw new Error("Satellite scene date was malformed");
    return { id: requiredString(scene.id, "scene ID"), acquiredAt,
      platform: scene.platform as string | null, sceneCloudCoverPercent: cloud as number | null };
  });
  return { checkedAt, scenes };
}

export async function loadObservations(): Promise<{ items: DemoObservation[]; fromApi: boolean }> {
  const response = await fetch(`${apiBase}/observations`, { headers: { Accept: "application/json" }, cache: "no-store" });
  if (!response.ok) throw new Error(`Observation request failed (${response.status})`);
  const payload: unknown = await response.json();
  const data = Array.isArray(payload)
    ? payload
    : payload && typeof payload === "object" && Array.isArray((payload as UnknownRecord).items)
      ? (payload as UnknownRecord).items as unknown[]
      : [];
  if (!data.length) throw new Error("Observation response contained no records");
  const items = data.filter((item): item is UnknownRecord => Boolean(item) && typeof item === "object").map(normalizeDemoObservation);
  if (!items.length) throw new Error("Observation response did not contain usable records");
  return { items, fromApi: true };
}

export async function createCase(observation: DemoObservation): Promise<{ id: string }> {
  const response = await fetch(`${apiBase}/cases`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      observation_id: observation.id,
      title: `Review record for ${observation.id}`,
      owner_organization: "Demo conservation review team",
      reviewer: "Demo analyst",
    }),
  });
  if (!response.ok) throw new Error(`Case creation failed (${response.status})`);
  const payload: unknown = await response.json();
  const result = payload && typeof payload === "object" ? payload as UnknownRecord : {};
  return { id: requiredString(result.id, "case ID") };
}

export type CaseAction = { id: string; actionType: string; summary: string; occurredAt: string; recordedBy: string };
export type CaseFollowUp = { id: string; assessment: string; summary: string; observedAt: string; recordedBy: string };
export type LoadedCase = { record: DemoCase; observation: DemoObservation; fromApi: boolean; actions: CaseAction[]; followUps: CaseFollowUp[] };

export async function loadCaseRecord(id: string): Promise<LoadedCase> {
  const response = await fetch(`${apiBase}/cases/${encodeURIComponent(id)}`, { headers: { Accept: "application/json" }, cache: "no-store" });
  if (!response.ok) throw new Error(`Case request failed (${response.status})`);
  const payload: unknown = await response.json();
  if (!payload || typeof payload !== "object") throw new Error("Case response was malformed");
  const raw = payload as UnknownRecord;
  if (typeof raw.id !== "string" || raw.id !== id) throw new Error("Case response did not match the requested case");
  const observationRaw = raw.observation;
  if (!observationRaw || typeof observationRaw !== "object") throw new Error("Case response omitted its observation");
  const observation = normalizeDemoObservation(observationRaw as UnknownRecord);
  if (!Array.isArray(raw.actions) || !Array.isArray(raw.follow_ups)) throw new Error("Case response omitted workflow records");
  const actions: CaseAction[] = raw.actions.map((item: unknown) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) throw new Error("Case action was malformed");
    const action = item as UnknownRecord;
    return { id: requiredString(action.id, "action ID"), actionType: requiredString(action.action_type, "action type"),
      summary: requiredString(action.summary, "action summary"), occurredAt: stringValue(action.occurred_at, ""),
      recordedBy: stringValue(action.recorded_by, "Unknown actor") };
  });
  const followUps: CaseFollowUp[] = raw.follow_ups.map((item: unknown) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) throw new Error("Case follow-up was malformed");
    const followUp = item as UnknownRecord;
    return { id: requiredString(followUp.id, "follow-up ID"), assessment: requiredString(followUp.assessment, "follow-up assessment"),
      summary: requiredString(followUp.summary, "follow-up summary"), observedAt: stringValue(followUp.observed_at, ""),
      recordedBy: stringValue(followUp.recorded_by, "Unknown actor") };
  });
  const rawEvents = Array.isArray(raw.events) ? raw.events : [];
  const timeline: TimelineEntry[] = rawEvents.filter((entry): entry is UnknownRecord => Boolean(entry) && typeof entry === "object").map((entry) => {
    const details = entry.payload && typeof entry.payload === "object" ? entry.payload as UnknownRecord : {};
    return {
      at: stringValue(entry.occurred_at, ""),
      label: stringValue(entry.event_type, "Case event").replaceAll("_", " "),
      detail: stringValue(details.note ?? details.summary ?? details.assessment, "Workflow event recorded."),
      actor: stringValue(entry.actor, "Unknown actor"),
    };
  });
  const record: DemoCase = {
    id: stringValue(raw.id, id),
    title: stringValue(raw.title, `Review record for ${observation.id}`),
    status: caseStatusFrom(raw.status),
    owner: stringValue(raw.owner_organization, "Unassigned"),
    priority: "Standard",
    observationId: observation.id,
    openedAt: stringValue(raw.created_at, ""),
    evidenceCount: Array.isArray(raw.evidence) ? raw.evidence.length : 0,
    timeline,
  };
  return { record, observation, fromApi: true, actions, followUps };
}

export async function transitionCase(caseId: string, toStatus: CaseStatus): Promise<void> {
  const response = await fetch(`${apiBase}/cases/${encodeURIComponent(caseId)}/transitions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ to_status: toStatus, actor: "Demo analyst", note: "Workflow transition recorded from the ForestProof P0 interface." }),
  });
  if (!response.ok) throw new Error(`Case transition failed (${response.status})`);
}

export async function recordDemoAction(caseId: string, summary: string): Promise<void> {
  const response = await fetch(`${apiBase}/cases/${encodeURIComponent(caseId)}/actions`, {
    method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ action_type: "DEMO_REVIEW", summary, actor: "Demo analyst" }),
  });
  if (!response.ok) throw new Error(`Action request failed (${response.status})`);
}

export type FollowUpAssessment = "VERIFIED_INCIDENT" | "FALSE_POSITIVE" | "INSUFFICIENT_EVIDENCE" | "UNRESOLVED";

export async function recordDemoFollowUp(caseId: string, assessment: FollowUpAssessment, summary: string): Promise<void> {
  const response = await fetch(`${apiBase}/cases/${encodeURIComponent(caseId)}/follow-ups`, {
    method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ assessment, summary, actor: "Demo analyst" }),
  });
  if (!response.ok) throw new Error(`Follow-up request failed (${response.status})`);
}

export async function attachDemoEvidence(caseId: string): Promise<void> {
  const content = "ForestProof P0 synthetic interface evidence. This file represents no real field observation.";
  const response = await fetch(`${apiBase}/cases/${encodeURIComponent(caseId)}/evidence`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      file_name: "demo-interface-note.txt",
      media_type: "text/plain",
      content_base64: btoa(content),
      source_description: "Synthetic P0 interface evidence fixture; not a field record.",
      actor: "Demo analyst",
    }),
  });
  if (!response.ok) throw new Error(`Evidence attachment failed (${response.status})`);
}

export async function fetchDossier(caseId: string): Promise<unknown> {
  const response = await fetch(`${apiBase}/cases/${encodeURIComponent(caseId)}/dossier`, { headers: { Accept: "application/json" }, cache: "no-store" });
  if (!response.ok) throw new Error(`Dossier request failed (${response.status})`);
  return response.json();
}
