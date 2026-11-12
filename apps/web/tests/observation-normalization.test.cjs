const assert = require("node:assert/strict");
const fs = require("node:fs");
const Module = require("node:module");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");

// Load the pure TypeScript module with the project's existing compiler.
const filename = path.join(__dirname, "../src/lib/observation-normalization.ts");
const source = fs.readFileSync(filename, "utf8");
const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const compiled = new Module(filename, module);
compiled.filename = filename;
compiled.paths = module.paths;
compiled._compile(js, filename);
const { normalizeDemoObservation } = compiled.exports;

const record = { id: "obs_test", quality_flags: ["DEMO_DATA"], geometry: { type: "Point", coordinates: [36.75, -0.38] } };

test("missing provenance and confidence stay unknown instead of borrowing another observation", () => {
  const result = normalizeDemoObservation(record);
  assert.equal(result.id, "obs_test");
  assert.deepEqual(result.coordinates, [36.75, -0.38]);
  assert.equal(result.source, "Not provided");
  assert.equal(result.sourceRecordId, "Not provided");
  assert.equal(result.publishedAt, "");
  assert.equal(result.confidenceScore, null);
  assert.deepEqual(result.qualityFlags, ["DEMO_DATA"]);
});

test("supplied source data and normalized confidence are preserved", () => {
  const result = normalizeDemoObservation({ ...record, source_id: "source-1", source_record_id: "cell-123", observed_at: "2026-01-01T00:00:00Z", confidence_value: 0.74 });
  assert.equal(result.source, "source-1");
  assert.equal(result.sourceRecordId, "cell-123");
  assert.equal(result.observedAt, "2026-01-01T00:00:00Z");
  assert.equal(result.confidenceScore, 74);
  assert.equal(result.publishedAt, "");
});

test("the demo UI rejects unlabelled records and records missing their own identity or position", () => {
  assert.throws(() => normalizeDemoObservation({ ...record, quality_flags: [] }), /demo observations/);
  assert.throws(() => normalizeDemoObservation({ ...record, id: "" }), /identifier/);
  assert.throws(() => normalizeDemoObservation({ ...record, geometry: null }), /coordinates/);
  assert.throws(() => normalizeDemoObservation({ ...record, geometry: { type: "Point", coordinates: [200, 0] } }), /coordinates/);
  assert.throws(() => normalizeDemoObservation({ ...record, geometry: { type: "Polygon", coordinates: [36, 0] } }), /coordinates/);
});

test("unknown or non-normalized confidence does not invent a percentage", () => {
  assert.equal(normalizeDemoObservation({ ...record, confidence_value: null }).confidenceScore, null);
  assert.equal(normalizeDemoObservation({ ...record, confidence_value: 80 }).confidenceScore, null);
});


test("versioned demo provenance is preserved without inventing missing attribution or release", () => {
  const item = { ...record, source_id: "demo-synthetic-v1", source_record_id: "DEMO-123" };
  const provenance = { contract_version: "1", data_mode: "DEMO", source_id: item.source_id,
    record_key: item.source_record_id, record_key_kind: "SYNTHETIC_FIXTURE",
    quality_flags: ["DEMO_DATA"], processing_version: "fixture-v1",
    source_release: null, completeness: "UNKNOWN", attribution: null };
  assert.deepEqual(normalizeDemoObservation({ ...item, source_provenance: provenance }).sourceProvenance, {
    processingVersion: "fixture-v1", sourceRelease: null, completeness: "UNKNOWN", attribution: null,
  });
  assert.equal(normalizeDemoObservation(item).sourceProvenance, undefined);
});

test("mixed, foreign, unknown, or malformed source provenance is rejected", () => {
  const item = { ...record, source_id: "demo-synthetic-v1", source_record_id: "DEMO-123" };
  const provenance = { contract_version: "1", data_mode: "DEMO", source_id: item.source_id,
    record_key: item.source_record_id, record_key_kind: "SYNTHETIC_FIXTURE",
    quality_flags: ["DEMO_DATA"], processing_version: "fixture-v1",
    source_release: null, completeness: "UNKNOWN", attribution: null };
  for (const changed of [
    { data_mode: "LIVE" }, { record_key_kind: "PROVIDER_NATIVE" },
    { record_key: "DEMO-OTHER" }, { source_id: "other-source" },
    { quality_flags: [] }, { processing_version: "" },
    { completeness: "COMPLETE" }, { contract_version: "2" },
  ]) {
    assert.throws(() => normalizeDemoObservation({ ...item, source_provenance: { ...provenance, ...changed } }), /provenance/);
  }
  assert.throws(() => normalizeDemoObservation({ ...item, source_provenance: null }), /provenance/);
});
