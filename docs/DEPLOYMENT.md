# Deployment

## Status

**HOSTED BETA PACKAGE READY.** A public deployment has not yet been created.
The approved launch path is a private GitHub repository plus Railway-managed web
and API services. The API remains DEMO-only and private behind the web service's
same-origin proxy.

## Local P0 target

- Web client and API run through Docker Compose or equivalent local commands, with a SQLite development adapter and private local evidence directory.
- The Compose `postgis` profile provisions PostGIS for schema inspection and future adapter work; the current API does not connect to it yet.
- Configuration is taken from an example environment file; secrets stay outside Git.
- DEMO mode runs without paid credentials.
- Tests cover the core workflow before any hosted demo is represented as reliable.

## Hosted beta path

1. Push to the owner's personal GitHub account as a private repository.
2. Create the Railway `api` service from `/services/api`; attach a `/data`
   persistent volume for the SQLite DEMO store and synthetic evidence files.
3. Create the public Railway `web` service from `/apps/web`; set its internal
   API URL to `http://api.railway.internal:8000/api/v1`.
4. Generate a public web domain; do not generate a public API domain.
5. Set the API's `WEB_ORIGIN` to the exact web domain and verify the review
   case, evidence, and dossier acceptance flow after a refresh.

The exact launch checklist is in [RAILWAY_LAUNCH.md](RAILWAY_LAUNCH.md).

## Production path after the beta

1. Replace the SQLite adapter with PostgreSQL/PostGIS and test migrations.
2. Move evidence to private object storage with encryption, lifecycle policy,
   backup, and restore drills.
3. Add authentication, role-based access control, rate limiting, and tenant
   isolation before accepting any real case material.
4. Enable only approved data-source credentials after validating terms,
   provenance, AOI coverage, and health monitoring.
5. Perform security, tenant-boundary, and restoration validation.

## Explicitly deferred

Kubernetes, Kafka, private global imagery mirrors, idle GPUs, public anonymous evidence access, and complex multi-region deployment are not P0 requirements.

## Deployment evidence

Before declaring a deployment WORKING, record environment, version, migration result, backup/restore test, source health, authenticated user journey result, known limitations, responsible operator, and date. Do not publish private source code or make production security changes without approval.
