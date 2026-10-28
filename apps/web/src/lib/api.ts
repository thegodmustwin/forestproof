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
  return typeof value === "string" && states.includes(value as CaseStatus) ? value as CaseStatus : "NEW";
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

export async function createCase(observation: DemoObservation): Promise<{ id?: string }> {
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
  return { id: typeof result.id === "string" ? result.id : undefined };
}

export type LoadedCase = { record: DemoCase; observation: DemoObservation; fromApi: boolean };

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
  return { record, observation, fromApi: true };
}

export async function transitionCase(caseId: string, toStatus: CaseStatus): Promise<void> {
  const response = await fetch(`${apiBase}/cases/${encodeURIComponent(caseId)}/transitions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ to_status: toStatus, actor: "Demo analyst", note: "Workflow transition recorded from the ForestProof P0 interface." }),
  });
  if (!response.ok) throw new Error(`Case transition failed (${response.status})`);
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
