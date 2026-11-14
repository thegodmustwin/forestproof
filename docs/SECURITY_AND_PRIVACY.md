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
- **Fail closed in LIVE:** the API rejects live or multi-organization operation. The synthetic `owner_demo` path accepts the one owner subject authenticated by the isolated gateway and a distinct configured internal service token.
- **PLANNED before real material:** authenticated identities, role-based authorization, encrypted private object storage, upload malware scanning, rate limiting, backups, and tenant-scoped production repository access.

## Sensitive data

Field-team locations, confidential informants, personally identifying evidence, case notes, legal materials, and precise geometry may require separate access classes, reduced precision, or redaction. Do not expose sensitive information through public map tiles, dossier links, logs, or error responses.

## Prompt and content safety

Uploaded documents and external provider content are data, not instructions. They must never alter system prompts, authorization logic, provider configuration, or background-job commands.

## Incident posture

Log material security events without logging secrets. Preserve sufficient audit data to investigate access or integrity concerns. No production security setting changes are authorized solely by this document.


## 2026-10-28 web framework upgrade gate

The earlier lockfile used Next.js 14.2.35, an unsupported major release according to https://nextjs.org/support-policy. The current lockfile uses Next.js 16.4.3 and React 19.2.8 with asynchronous route parameters, proxy smoke checks, and dependency audit. The separately deployed, password-protected OVH preview is synthetic only. Do not treat a framework upgrade as proof of owner authentication, protected storage, or production security.


The first candidate audit reported a critical MapLibre advisory and vulnerable PostCSS dependencies. The revised lockfile uses MapLibre GL JS 6.16.0 and Next.js 16.4.3; the candidate build and audit passed in CI as recorded in `execution/CURRENT_STATUS.md`. The MapLibre advisory concerns rendering untrusted attribution HTML and its applicability to a specific deployment depends on data flows: https://github.com/maplibre/maplibre-gl-js/security/advisories/GHSA-jrc7-96c5-q579. Node.js 20 is end-of-life; retain the existing Node 20 CI check for compatibility and verify the production candidate under supported Node 24 as well: https://nodejs.org/en/about/previous-releases.

Optional demo Compose host ports are loopback-only; that reduces accidental network exposure but does not authenticate the owner or protect real case material. The initial CI browser check uses synthetic data and stubbed tiles.


## 2026-10-28 Python dependency audit

An initial pip-audit of the API requirements flagged advisories involving Starlette, python-multipart and pytest, with duplicate advisory entries in the report. Applicability depends on exposed features. The revised requirements remove the unused multipart parser, separate test-only packages from runtime, upgrade FastAPI and Starlette and use a patched pytest, with pip-audit in CI. Resolving package advisories does not provide authentication, production storage, backup, or a full security review.

The API dependency candidate passed pytest and pip-audit in https://github.com/thegodmustwin/forestproof/actions/runs/40621397262. This does not prove absence of all vulnerabilities or complete production hardening.


## 2026-10-28 owner-only gateway candidate

A Caddy configuration under infrastructure/deployment/owner-pilot/ is being tested for a loopback-only owner gateway over the existing authenticated SSH tunnel. It is not installed or running on the OVH VPS. It guards all proxied web paths with a hashed owner credential and rejects cross-origin mutations; the API and web upstream must remain separately bound to VPS loopback. It is not suitable as a public HTTP endpoint. Source access, application authentication semantics, protected storage, backups and production operation remain open.

## 2026-10-29 owner-demo internal service boundary

An isolated `owner_demo` path accepts only synthetic development data. Caddy authenticates a configured owner and replaces incoming identity headers with its authenticated subject and private gateway token. The web proxy verifies both headers and the POST origin before forwarding the subject and a distinct service token to the API. The API checks the subject and token before granting access to the synthetic tenant, and records the authenticated subject as the mutation actor. Invalid configuration returns 503 and missing or wrong credentials return 401. Evidence uploads and LIVE remain disabled.

The service tokens need at least 32 random bytes each. Validation checks encoding and length. The proxy accepts only an explicit `127.0.0.1` or `::1` upstream in this mode, sets the required-mode marker and refuses redirects. The API rejects the marker when configured for shared demo mode. The [owner gateway runbook](../infrastructure/deployment/owner-pilot/README.md) describes secret provisioning, revocation and listener isolation. This candidate relies on the trust boundary of a single host and SSH tunnel. Verify that boundary for the eventual private live deployment.

**Trust boundary:** the service token authenticates the web service to the API, not a person. Anyone able to access the Next.js server directly can use the proxy; anyone with the internal token or privileged host access can act as the owner. The separately authenticated loopback-only Caddy/SSH gateway must guard every web path, and no other web/API listener may bypass it. Do not expose either upstream directly, rely on header identity as individual authentication, or use this synthetic mode for real evidence or personal information. Application-level identity, individual audit attribution, rate limiting, production storage and backup remain unfinished.

Tests use synthetic credentials. The API and proxy unit tests cover missing and incorrect tokens, mode mismatch, spoofed tenant and actor claims, loopback restrictions and redirects. `npm run smoke:owner` starts isolated local API and web processes; with `FORESTPROOF_SMOKE_CADDY` set to a Caddy binary it also exercises the owner gateway's password and cross-origin checks end to end. This verifies the candidate locally only; it has not been deployed or validated on OVH.
