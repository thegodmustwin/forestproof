# Launch ForestProof on Railway

> **Historical and superseded:** The owner has since selected OVH as the
> preferred production host. Do not use this guide as the current launch path
> or create Railway resources unless the owner changes that decision. See
> [DEPLOYMENT.md](DEPLOYMENT.md) for the verified status and OVH prerequisites.

This document preserves an earlier proposed hosted-beta path for reference.
Its instructions have not been executed or approved as the current deployment.

ForestProof remains in `DEMO` mode on this path. It contains deterministic,
labelled fixtures and allows users to exercise the evidence and case workflow.
It does **not** activate live satellite, permit, legal, or enforcement feeds.

## Before you start

- Push this repository to the personal GitHub account you intend to own it.
- Create or sign in to a Railway account using that same GitHub account.
- Choose a paid Railway plan or confirm that your plan supports a persistent
  volume. The API's SQLite data and labelled synthetic evidence files must live
  on that volume; an ephemeral filesystem is not an acceptable deployment.

## Create the API service

1. In Railway, create a project and choose **Deploy from GitHub repo**.
2. Name the service `api`, select the ForestProof repository, and set its root
   directory to `/services/api`.
3. Railway detects `services/api/Dockerfile`. Do not generate a public domain
   for this service: the web application reaches it over Railway private
   networking.
4. Add a persistent volume mounted at `/data`.
5. In the API service Variables tab, add these non-secret values:

   ```text
   FORESTPROOF_MODE=demo
   FORESTPROOF_SQLITE_PATH=/data/forestproof.db
   EVIDENCE_STORAGE_PATH=/data/evidence
   WEB_ORIGIN=https://placeholder.invalid
   ```

6. Deploy the service and confirm its health check reports `status: ok` in the
   Railway deployment log. It listens on Railway's provided `PORT`.

Keep this API at one replica while it uses SQLite on one attached volume. Do not
turn on horizontal scaling for this hosted beta; the production migration to
PostgreSQL/PostGIS is the prerequisite for that change.

## Create the public web service

1. Add a second service from the same GitHub repository and name it `web`.
2. Set its root directory to `/apps/web`. Railway uses the production Dockerfile
   and creates a Next.js production build remotely.
3. Add this service variable exactly (the API service must be named `api`):

   ```text
   FORESTPROOF_API_INTERNAL_BASE_URL=http://api.railway.internal:8000/api/v1
   NEXT_PUBLIC_ENABLE_GFW_GLAD_S2_CONTEXT=false
   ```

   Do **not** set `NEXT_PUBLIC_API_BASE_URL` for Railway. When it is absent, the
   browser calls the same-origin Next.js proxy, which forwards only `GET` and
   `POST` requests over Railway's private network.

4. Generate a Railway public domain for `web`, then open it in a browser.
5. Replace the API service's `WEB_ORIGIN` value with the exact `https://...`
   web domain and redeploy the API. This keeps CORS correct for future browser
   integrations, even though the hosted UI uses the private proxy today.

## Acceptance check

At the public `web` URL:

1. Open **Monitor / Aberdare** and verify the banner says the API is connected.
2. Select an observation and create a review record.
3. Open the record, progress it through the permitted workflow, attach the
   labelled synthetic evidence item, and download a dossier.
4. Refresh the page and confirm the record remains. This validates the API
   volume rather than an in-memory or browser-only demo.

## What makes this a hosted beta, not production

- The API is deliberately DEMO-only and does not authenticate individual users.
- SQLite plus a single attached volume is suitable for an early hosted beta,
  not concurrent multi-organization operation.
- Enable and test a volume backup/restore workflow before treating stored case
  history as anything beyond a demonstration record.
- Real operation requires authenticated roles, a PostgreSQL/PostGIS repository
  adapter, private object storage, backups/restore drills, and approved source
  credentials with terms checked for the actual area of interest.
- Never add live-source keys to the Git repository. Put them in Railway
  Variables only after the source terms and provenance workflow are approved.

Railway's [monorepo deployment guide](https://docs.railway.com/deployments/monorepo),
[volume documentation](https://docs.railway.com/volumes), and
[variables documentation](https://docs.railway.com/variables) describe the
underlying managed-service configuration.
