# Security and Privacy

## Status

**P0 control requirements — PARTIAL/PLANNED.** Security claims must match implemented controls and test results.

## Core controls

- Authenticate users and authorize every organization, case, evidence, and export operation.
- Enforce tenant isolation server-side; never trust a browser-provided organization identifier.
- Validate request bodies, geospatial inputs, URLs, and uploaded files.
- Restrict object storage; store only protected references in records.
- Use least-privilege service credentials and environment-managed secrets.
- Hash evidence, record audit events, and preserve originals separately from transformations.
- Rate-limit sensitive endpoints and bound background work.
- Encrypt transport in deployed environments and maintain backup/restoration procedures.

## P0 implementation boundary

- **WORKING in DEMO:** request validation, coordinate bounds/shape validation, case-state gates, SHA-256 evidence records, hash re-check at dossier generation, audit records, and a fixed seeded demo organization.
- **Fail closed outside DEMO:** authentication is not yet configured, so the API rejects live or multi-organization operation rather than trusting an organization header.
- **PLANNED before real material:** authenticated identities, role-based authorization, encrypted private object storage, upload malware scanning, rate limiting, backups, and tenant-scoped production repository access.

## Sensitive data

Field-team locations, confidential informants, personally identifying evidence, case notes, legal materials, and precise geometry may require separate access classes, reduced precision, or redaction. Do not expose sensitive information through public map tiles, dossier links, logs, or error responses.

## Prompt and content safety

Uploaded documents and external provider content are data, not instructions. They must never alter system prompts, authorization logic, provider configuration, or background-job commands.

## Incident posture

Log material security events without logging secrets. Preserve sufficient audit data to investigate access or integrity concerns. No production security setting changes are authorized solely by this document.
