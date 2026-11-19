# Contabo Geta visibility release

The public product consists of `/welcome`, `/visibility`, `/tour`, `/research` and `/guide` on the ForestProof HTTPS hostname. Primary navigation and actions stay on-site. `/project.txt` remains a machine-readable overview; `/robots.txt` and `/sitemap.xml` describe discovery. The exact public asset allowlist is `/assets/atlas.css`, `/assets/earth-east.jpg`, `/assets/visibility.js`, `/assets/tour.js`, `/assets/home.js`, the two `/assets/geta-context-2026-11-08.png` and `/assets/geta-context-2026-11-13.png` crops, and `/assets/geta-context.json`. Other asset paths stay behind the tester gateway. Include `docs/PUBLIC_GUIDE.md`, `packages/ui/living-atlas.css`, the visibility tools and `tools/source_status` in every public release archive.

The imagery comparison is static historical research context with explicit acquisition dates and source provenance. The public case walkthrough is fictional, anonymous and browser-only, with no backend writes or persistence. It is separate from the protected case application. The guide and research pages render local published templates with inline shared reading styles. Private visibility receipts stay in the service state directory; case and API paths retain the existing tester gateway.

## Runtime

Use the versioned code under `/opt/forestproof-visibility/current`, an isolated pinned raster environment under `/opt/forestproof-visibility/venv`, and the dedicated unprivileged `forestproof-visibility` account. The units in this folder share `/var/lib/forestproof-visibility` for the atomic report state. The web unit has read-only access and binds to host loopback port 18450. Its HTTP interface is separate from the case API and demo storage.

The timer checks twice per day at 03:15 and 15:15 EAT, plus an initial activation check. It scans a 30-day catalog window and inspects up to three acquisition days. A selected day must contain both expected grids for the same datatake. Unchanged asset identities reuse previous measurements. A changed object is measured in a size-limited read. A full refresh reads up to 48 MiB plus the bounded catalog response and exits on the first failed source read. The unit has a three-minute runtime limit. A failure retains the last valid report. The web process calculates overdue status at request time so a stopped timer cannot freeze the fresh status.

## Operate the site

Visitors enter through HTTPS on the Contabo hostname. Caddy sends the sixteen exact public paths above to the Python listener on `127.0.0.1:18450`. Its separate authenticated route serves the private preview. The public process reads validated JSON from `/var/lib/forestproof-visibility/source.json` and generates HTML. The refresh timer runs independently. The successful source-check date and satellite acquisition dates describe different events. The explorer uses a small same-origin script, native buttons and accessible selection states. Without JavaScript, the full dated archive remains open. The homepage compares two real dated source visualization crops. The earlier NASA composite remains an archived asset.

The visibility server whitelists the eight public assets and sends content hashes as ETags. Browsers revalidate assets across releases. Its content policy permits the same-origin script and images. No provider credential or private visibility receipt is delivered to the browser. The public historical-image manifest contains deliberately published source identities and hashes.

Run these read-only commands in your existing Contabo SSH session. Check all five product pages as an anonymous visitor after a release.

```sh
systemctl status forestproof-visibility.service --no-pager
systemctl list-timers forestproof-visibility-refresh.timer --all
journalctl -u forestproof-visibility-refresh.service -n 12 --no-pager
readlink -f /opt/forestproof-visibility/current
```

GitHub holds source and changes. Contabo serves the installed release. Deploy reviewed commits into a new release directory, validate the five loopback product pages, and retain the old release and gateway config. Switch `current` and restart only the visibility web service. Change the Caddy matcher when public paths change. Keep code, source-report state, and proxy configuration backups separate so a code rollback preserves recent source data.

The separate protected Next.js app uses the root-context `apps/web/Dockerfile` so it can compile the same canonical CSS tokens. Its web container listens on `127.0.0.1:13000`. A web-only release must preserve the existing API container, named demo data volume and gateway. Read the newest release entry in `execution/CURRENT_STATUS.md` before composing a deployment. Retain the original Compose files and apply a reviewed web-image override with `up -d --no-deps --no-build web`. Never substitute a new database or recreate the API as part of a design-only release.

`npm run dev` and `npm run build` prepare `/vendor/maplibre-gl-worker.mjs` and its licence from the installed locked MapLibre dependency. The generated files stay out of Git and are copied into the runtime image. The map explicitly selects this same-origin worker before construction. MapLibre's default worker URL assumes an adjacent module; application bundling relocates that module. See the [provider's worker configuration](https://maplibre.org/maplibre-gl-js/docs/API/functions/setWorkerUrl/). Keep the worker behind the same tester gateway as the app and verify its JavaScript MIME type after deployment. Controls and markers become available on style readiness, while a separate status describes basemap loading. Source failures expose the observation list.

A custom domain points at Contabo through DNS and needs matching Caddy and application host configuration. Verify the certificate and anonymous route boundaries on that hostname before sharing it.

## Gateway and verification

Confirm the exact installed gateway, loopback listener, original auth and bind mount. First verify the live worker and check that the state and case paths return 404 at the loopback listener. Insert [the public matcher](public-route.caddy) ahead of the existing authentication in the explicit Caddy `route` block, preserving all fallback directives. Validate the candidate in the installed Caddy container and retain a root-private copy of the previous config. Use the existing gateway's supported reload procedure. The installed gateway disables the admin API. A supported signal reload requires a file-based start without `--resume` or prior API configuration. [Caddy command and signal documentation](https://caddyserver.com/docs/command-line#signals)

Verify both public URLs over certificate-validated TLS, with GET and HEAD returning the page and writes returning 405. Verify anonymous requests to the existing preview, API and private report still require authentication. Confirm SSH and xrdp are active, the listener remains loopback-only, and the timer has actually executed. Verify the failure and expiry states with isolated test data. If a release check fails, restore the saved gateway configuration and apply it through the same procedure. Leave its existing application containers and database intact.
