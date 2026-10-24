-- ForestProof PostGIS schema target. The P0 API deliberately runs the matching
-- SQLite development adapter; do not set POSTGIS_DATABASE_URL until a tested
-- Postgres repository adapter is delivered. IDs and field names here mirror the
-- P0 repository contract so that adapter work is additive rather than a rewrite.
-- Geometry is stored in EPSG:4326 and is retained alongside original GeoJSON.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE organizations (
  id text PRIMARY KEY,
  name text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE monitored_areas (
  id text PRIMARY KEY,
  organization_id text NOT NULL REFERENCES organizations(id),
  name text NOT NULL,
  geometry geometry(Geometry, 4326) NOT NULL,
  source_reference text NOT NULL,
  boundary_status text NOT NULL CHECK (boundary_status IN ('DEMO', 'VERIFIED', 'UNVERIFIED')),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX monitored_areas_geometry_gix ON monitored_areas USING gist (geometry);

CREATE TABLE data_sources (
  id text PRIMARY KEY,
  source_name text NOT NULL,
  official_organization text NOT NULL,
  source_url text,
  documentation_url text,
  operational_status text NOT NULL,
  license text,
  limitations text NOT NULL,
  verified_at timestamptz
);

CREATE TABLE observations (
  id text PRIMARY KEY,
  organization_id text NOT NULL REFERENCES organizations(id),
  source_id text NOT NULL REFERENCES data_sources(id),
  source_product text NOT NULL,
  source_record_id text NOT NULL,
  observed_at timestamptz NOT NULL,
  published_at timestamptz,
  ingested_at timestamptz NOT NULL,
  observation_type text NOT NULL,
  classification text NOT NULL,
  confidence_value numeric CHECK (confidence_value IS NULL OR (confidence_value >= 0 AND confidence_value <= 1)),
  confidence_meaning text,
  spatial_resolution_meters numeric,
  geometry_json jsonb NOT NULL,
  geometry geometry(Geometry, 4326),
  forest_classification text,
  processing_version text NOT NULL,
  raw_evidence_ref text,
  quality_flags_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (source_id, source_record_id, processing_version)
);
CREATE INDEX observations_geometry_gix ON observations USING gist (geometry);
CREATE INDEX observations_org_time_idx ON observations (organization_id, observed_at DESC);

CREATE OR REPLACE FUNCTION forestproof_sync_observation_geometry()
RETURNS trigger AS $$
BEGIN
  NEW.geometry := ST_SetSRID(ST_GeomFromGeoJSON(NEW.geometry_json::text), 4326);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER observations_sync_geometry
  BEFORE INSERT OR UPDATE OF geometry_json ON observations
  FOR EACH ROW EXECUTE FUNCTION forestproof_sync_observation_geometry();

CREATE TABLE investigation_cases (
  id text PRIMARY KEY,
  organization_id text NOT NULL REFERENCES organizations(id),
  observation_id text NOT NULL REFERENCES observations(id),
  title text NOT NULL,
  status text NOT NULL CHECK (status IN ('NEW','UNDER_REVIEW','FIELD_VERIFICATION','ACTION_RECORDED','FOLLOW_UP','CLOSED','REOPENED')),
  owner_organization text NOT NULL,
  reviewer text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, observation_id)
);
CREATE INDEX cases_org_status_idx ON investigation_cases (organization_id, status, updated_at DESC);

CREATE TABLE evidence_assets (
  id text PRIMARY KEY,
  case_id text NOT NULL REFERENCES investigation_cases(id),
  storage_key text NOT NULL UNIQUE,
  file_name text NOT NULL,
  media_type text NOT NULL,
  byte_size bigint NOT NULL CHECK (byte_size >= 0),
  sha256 char(64) NOT NULL,
  source_description text NOT NULL,
  observed_at timestamptz,
  uploaded_at timestamptz NOT NULL DEFAULT now(),
  uploaded_by text NOT NULL,
  integrity_status text NOT NULL DEFAULT 'PENDING'
);

CREATE TABLE case_events (
  id text PRIMARY KEY,
  case_id text NOT NULL REFERENCES investigation_cases(id),
  event_type text NOT NULL,
  actor text NOT NULL,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  payload_json jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX case_events_case_time_idx ON case_events (case_id, occurred_at);

CREATE TABLE case_assignments (
  id text PRIMARY KEY,
  case_id text NOT NULL REFERENCES investigation_cases(id),
  assignee text NOT NULL,
  role text NOT NULL,
  assigned_by text NOT NULL,
  assigned_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE case_actions (
  id text PRIMARY KEY,
  case_id text NOT NULL REFERENCES investigation_cases(id),
  action_type text NOT NULL,
  summary text NOT NULL,
  occurred_at timestamptz NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  recorded_by text NOT NULL
);
CREATE TABLE follow_up_assessments (
  id text PRIMARY KEY,
  case_id text NOT NULL REFERENCES investigation_cases(id),
  assessment text NOT NULL CHECK (assessment IN ('VERIFIED_INCIDENT','FALSE_POSITIVE','INSUFFICIENT_EVIDENCE','UNRESOLVED')),
  summary text NOT NULL,
  observed_at timestamptz NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  recorded_by text NOT NULL
);

CREATE TABLE legal_documents (
  id text PRIMARY KEY,
  organization_id text NOT NULL REFERENCES organizations(id),
  document_type text NOT NULL,
  issuing_authority text,
  case_reference text,
  effective_from timestamptz,
  effective_to timestamptz,
  geographic_scope geometry(Geometry, 4326),
  source_url text NOT NULL,
  sha256 char(64),
  verification_status text NOT NULL CHECK (verification_status IN ('UNVERIFIED','HUMAN_VERIFIED','SUPERSEDED')),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX legal_documents_scope_gix ON legal_documents USING gist (geographic_scope);

-- The API must write audit entries transactionally. Hash chaining, digital signatures,
-- retention controls, and object-storage immutability are deployment policies layered
-- over this table; a hash alone does not prove the truth of source material.
CREATE TABLE audit_events (
  id text PRIMARY KEY,
  organization_id text NOT NULL REFERENCES organizations(id),
  aggregate_type text NOT NULL,
  aggregate_id text NOT NULL,
  action text NOT NULL,
  actor text NOT NULL,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX audit_events_aggregate_idx ON audit_events (aggregate_type, aggregate_id, occurred_at);
