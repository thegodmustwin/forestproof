import { CaseStatus, DemoCase, DemoObservation, ObservationStatus, TimelineEntry, observations as demoObservations } from "@/lib/demo";

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

function numericValue(value: unknown, fallback: number): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function coordinatesFrom(record: UnknownRecord, fallback: [number, number]): [number, number] {
  const geometry = record.geometry as UnknownRecord | undefined;
  const coordinates = geometry?.coordinates ?? record.coordinates;
  if (Array.isArray(coordinates) && coordinates.length >= 2 && typeof coordinates[0] === "number" && typeof coordinates[1] === "number") {
    return [coordinates[0], coordinates[1]];
  }
  return fallback;
}

function statusFrom(value: unknown): ObservationStatus {
  const statuses: ObservationStatus[] = [
    "REQUIRES_HUMAN_REVIEW",
    "AUTHORIZATION_UNKNOWN",
    "DOCUMENTED_AUTHORIZATION",
    "INSUFFICIENT_EVIDENCE",
    "FALSE_POSITIVE",
  ];
  return typeof value === "string" && statuses.includes(value as ObservationStatus)
    ? value as ObservationStatus
    : "REQUIRES_HUMAN_REVIEW";
}

function caseStatusFrom(value: unknown): CaseStatus {
  const states: CaseStatus[] = ["NEW", "UNDER_REVIEW", "FIELD_VERIFICATION", "ACTION_RECORDED", "FOLLOW_UP", "CLOSED", "REOPENED"];
  return typeof value === "string" && states.includes(value as CaseStatus) ? value as CaseStatus : "NEW";
}

function normalizeObservation(record: UnknownRecord, index: number): DemoObservation {
  const fallback = demoObservations[index % demoObservations.length];
  const rawConfidence = numericValue(record.confidence_value, fallback.confidenceScore);
  const qualityFlags = Array.isArray(record.quality_flags)
    ? record.quality_flags.filter((item): item is string => typeof item === "string")
    : fallback.qualityFlags;
  return {
    id: stringValue(record.id, fallback.id),
    title: stringValue(record.title, fallback.title),
    source: stringValue(record.source_name ?? record.source, fallback.source),
    product: stringValue(record.source_product ?? record.product, fallback.product),
    sourceRecordId: stringValue(record.source_record_id, fallback.sourceRecordId),
    observedAt: stringValue(record.observed_at, fallback.observedAt),
    publishedAt: stringValue(record.published_at, fallback.publishedAt),
    ingestedAt: stringValue(record.ingested_at, fallback.ingestedAt),
    coordinates: coordinatesFrom(record, fallback.coordinates),
    confidence: stringValue(record.confidence_meaning, fallback.confidence),
    confidenceScore: rawConfidence >= 0 && rawConfidence <= 1 ? Math.round(rawConfidence * 100) : rawConfidence,
    classification: stringValue(record.observation_type ?? record.classification, fallback.classification),
    status: statusFrom(record.review_status ?? record.status ?? record.classification),
    forestClass: stringValue(record.forest_classification, fallback.forestClass),
    spatialResolution: typeof record.spatial_resolution_meters === "number"
      ? `${record.spatial_resolution_meters} m`
      : fallback.spatialResolution,
    qualityFlags,
    note: stringValue(record.interpretation_note ?? record.note, fallback.note),
  };
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
  const items = data.filter((item): item is UnknownRecord => Boolean(item) && typeof item === "object").map(normalizeObservation);
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
  const observationRaw = raw.observation;
  if (!observationRaw || typeof observationRaw !== "object") throw new Error("Case response omitted its observation");
  const observation = normalizeObservation(observationRaw as UnknownRecord, 0);
  const rawEvents = Array.isArray(raw.events) ? raw.events : [];
  const timeline: TimelineEntry[] = rawEvents.filter((entry): entry is UnknownRecord => Boolean(entry) && typeof entry === "object").map((entry) => {
    const details = entry.payload && typeof entry.payload === "object" ? entry.payload as UnknownRecord : {};
    return {
      at: stringValue(entry.occurred_at, observation.ingestedAt),
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
    openedAt: stringValue(raw.created_at, observation.ingestedAt),
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
