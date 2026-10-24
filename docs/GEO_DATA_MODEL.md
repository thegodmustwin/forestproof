# Geospatial Data Model

## Status

**PARTIAL.** The executable P0 SQLite adapter persists `observations`, `investigation_cases`, `case_events`, `evidence_assets`, `case_assignments`, `case_actions`, `follow_up_assessments`, and `audit_events`. It stores validated GeoJSON, not spatial indexes. PostGIS remains the intended spatial engine; the aligned target migration is supplied but no Postgres repository adapter is active.

## Target complete schema

| Domain | P0 records | Why |
| --- | --- | --- |
| Tenancy | organizations, users, memberships, roles | ownership and access scope |
| Geography | monitored_areas, land_classifications, catchment_areas, protected_area_boundaries | approved AOI and context |
| Sources | data_sources, source_products, ingestion_jobs, ingestion_events, source_health | provenance and operational health |
| Observations | environmental_observations, observation_geometries, observation_relations | original alert and related/duplicate context |
| Cases | investigation_cases, case_observations, case_assignments, case_status_events, case_notes | human workflow and audit trail |
| Evidence | evidence_assets, evidence_provenance, evidence_integrity_records, field_reports | defensible records |
| Context | legal_documents, legal_document_versions, legal_geographic_scopes, authorization_evidence | time-aware references |
| Actions/outcomes | intervention_actions, follow_up_observations, outcome_assessments, outcome_evidence | closed outcome loop |
| Audit | audit_events | immutable accountability trail |

## Spatial conventions

- Store operational geometry in a documented coordinate reference system, ordinarily WGS84 geometry for interchange.
- Use PostGIS spatial indexes for monitored areas and observation geometries.
- Calculate area with geography or a suitable projected CRS; never rely on degrees-squared area.
- Preserve provider geometry and normalized geometry separately if normalization changes representation.
- Associate an observation to an AOI through an explicit spatial relationship and recorded method/version.

## Observation relationships

observation_relations documents rather than hides links such as duplicate candidate, spatial overlap, temporal overlap, clustering, corroboration, contradiction, and derived-from. A second product is not automatically independent corroboration.

## Data minimization

Sensitive field coordinates, identities, and confidential evidence may require reduced precision or stricter access classification. Do not expose precise locations merely because the database can store them.

## Migration discipline

Add tables only when a P0 workflow needs them. Every migration must be reversible where practical, tenant-scoped where relevant, indexed for its expected spatial query, and covered by tests for geometry and access boundaries.
