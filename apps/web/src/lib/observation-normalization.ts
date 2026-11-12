import type { DemoObservation, ObservationStatus, SourceProvenance } from "./demo";

type UnknownRecord = Record<string, unknown>;

function text(value: unknown, fallback: string): string {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function reviewStatus(value: unknown): ObservationStatus {
  const statuses: ObservationStatus[] = ["REQUIRES_HUMAN_REVIEW", "AUTHORIZATION_UNKNOWN", "DOCUMENTED_AUTHORIZATION", "INSUFFICIENT_EVIDENCE", "FALSE_POSITIVE"];
  return typeof value === "string" && statuses.includes(value as ObservationStatus)
    ? value as ObservationStatus : "REQUIRES_HUMAN_REVIEW";
}

/** Parse an optional versioned API source contract without promoting mixed records. */
function demoProvenance(record: UnknownRecord): SourceProvenance | undefined {
  const value = record.source_provenance;
  // Older demo servers and local fixtures do not provide the new contract.
  if (value === undefined) return undefined;
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Source provenance was malformed");
  const source = value as UnknownRecord;
  const optionalText = (item: unknown) => item === null || (typeof item === "string" && item.trim().length > 0);
  if (source.contract_version !== "1" || source.data_mode !== "DEMO" ||
      source.record_key_kind !== "SYNTHETIC_FIXTURE" ||
      typeof source.record_key !== "string" || !source.record_key.trim() ||
      source.record_key !== record.source_record_id ||
      typeof source.source_id !== "string" || source.source_id !== record.source_id ||
      !Array.isArray(source.quality_flags) || !source.quality_flags.includes("DEMO_DATA") ||
      typeof source.processing_version !== "string" || !source.processing_version.trim() ||
      !optionalText(source.source_release) || !optionalText(source.attribution) ||
      source.completeness !== "UNKNOWN") {
    throw new Error("Source provenance did not match this demo observation");
  }
  return {
    processingVersion: source.processing_version,
    sourceRelease: source.source_release as string | null,
    completeness: "UNKNOWN",
    attribution: source.attribution as string | null,
  };
}

/** This UI is a demo. Reject other records until a real-source display is implemented. */
export function normalizeDemoObservation(record: UnknownRecord): DemoObservation {
  const flags = Array.isArray(record.quality_flags)
    ? record.quality_flags.filter((item): item is string => typeof item === "string") : [];
  if (!flags.includes("DEMO_DATA")) throw new Error("Only explicitly labelled demo observations are supported");
  const id = text(record.id, "");
  if (!id) throw new Error("Observation has no identifier");
  const geometry = record.geometry && typeof record.geometry === "object" ? record.geometry as UnknownRecord : undefined;
  const point = geometry?.coordinates ?? record.coordinates;
  if ((geometry && geometry.type !== "Point") || !Array.isArray(point) || point.length !== 2 ||
      typeof point[0] !== "number" || !Number.isFinite(point[0]) || Math.abs(point[0]) > 180 ||
      typeof point[1] !== "number" || !Number.isFinite(point[1]) || Math.abs(point[1]) > 90) {
    throw new Error("Observation has no valid point coordinates");
  }
  const score = record.confidence_value;
  const confidenceScore = typeof score === "number" && Number.isFinite(score) && score >= 0 && score <= 1
    ? Math.round(score * 100) : null;
  return {
    id,
    title: text(record.title, text(record.observation_type, "Observation")),
    source: text(record.source_name ?? record.source ?? record.source_id, "Not provided"),
    product: text(record.source_product ?? record.product, "Not provided"),
    sourceRecordId: text(record.source_record_id, "Not provided"),
    sourceProvenance: demoProvenance(record),
    observedAt: text(record.observed_at, ""),
    publishedAt: text(record.published_at, ""),
    ingestedAt: text(record.ingested_at, ""),
    coordinates: [point[0], point[1]],
    confidence: text(record.confidence_meaning, "Not provided"),
    confidenceScore,
    classification: text(record.observation_type ?? record.classification, "Not provided"),
    status: reviewStatus(record.review_status ?? record.status ?? record.classification),
    forestClass: text(record.forest_classification, "Not provided"),
    spatialResolution: typeof record.spatial_resolution_meters === "number" && Number.isFinite(record.spatial_resolution_meters) && record.spatial_resolution_meters > 0
      ? `${record.spatial_resolution_meters} m` : "Not provided",
    qualityFlags: flags,
    note: text(record.interpretation_note ?? record.note, "No interpretation was provided."),
  };
}
