# EvidenceProof Model

## Status

**PARTIAL.** P0 stores a local development object, SHA-256 digest, size, source description, and audit event; dossier generation re-hashes finalized objects. Upload malware scanning, access classes, retention policy, transformed derivatives, and production object storage are planned before real evidence is accepted.

## Purpose

EvidenceProof is the structured, inspectable record for an investigation case. It supports review and reporting; it is not a legal ruling or an assertion that supplied material is true.

## Required dossier contents

1. Case identifier and organization context.
2. Observation identifiers, source, timestamps, geometry, resolution, method, and quality flags.
3. Source methodology and processing versions.
4. Land-cover and monitored-area context.
5. Before/after imagery references only when suitable aligned imagery exists.
6. Legal-source references and authorization-evidence status.
7. Field reports, notes, supporting documents, and unresolved questions.
8. Assignments, state transitions, interventions, follow-up observations, and outcome assessment.
9. Evidence manifest with integrity metadata and access classification.

## Evidence asset record

Each uploaded or referenced asset records:

    evidence_id
    source
    uploader_id
    upload_time
    observation_time (optional)
    file_hash_sha256
    file_size
    mime_type
    storage_reference
    processing_version
    retention_policy
    access_classification

The original file stays separate from previews or transformed derivatives. A hash proves bytes match a recorded digest; it does not establish where a photo was taken or whether its contents are true.

## Evidence levels

All UI and export language should distinguish:

- **Observed:** an authenticated source reports it.
- **Derived:** deterministic processing calculated it.
- **Inferred:** a model or analyst interpreted it.
- **Verified:** an authorized review established it under documented criteria.
- **Unknown:** available evidence cannot establish it.
- **Disputed:** conflicting evidence or claims remain unresolved.

## Integrity and access

- Hash on ingest, persist metadata, and re-check integrity where applicable.
- Record creator, actor, timestamp, version, and transformation for material changes.
- Apply case and organization access control before serving original files.
- In production, scan and validate uploads before accepting them; P0 validates base64 encoding, filename, and a 10 MiB size limit only.
- Keep an append-only audit event for attachment, access-sensitive change, or deletion request.

## P0 output

P0 emits a structured JSON dossier endpoint with an explicit verification notice and per-asset `HASH_VERIFIED`, `HASH_MISMATCH`, `MISSING_OBJECT`, or pending status. HTML/PDF rendering is planned. Missing evidence is reported as missing, never silently fabricated.
