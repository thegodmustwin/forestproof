# Contabo Geta visibility release

The approved public pages are `/welcome` and `/visibility` on the ForestProof HTTPS hostname. `/project.txt` serves the public product guide, and `/robots.txt` and `/sitemap.xml` expose the public routes. The Living Atlas release also allows exactly `/assets/atlas.css`, `/assets/earth-east.jpg` and `/assets/visibility.js`. Other asset paths stay behind the tester gateway. Include `docs/PUBLIC_GUIDE.md`, `packages/ui/living-atlas.css`, the visibility tools and `tools/source_status` in every public release archive. The homepage introduces the provisional Geta research area and links to the dated pass explorer. The report publishes two overlapping native Sentinel-2 grid counts with Copernicus attribution. The private source receipts stay in the service state directory. Alert and case routes require the existing tester gateway.

## Runtime

Use the versioned code under `/opt/forestproof-visibility/current`, an isolated pinned raster environment under `/opt/forestproof-visibility/venv`, and the dedicated unprivileged `forestproof-visibility` account. The units in this folder share `/var/lib/forestproof-visibility` for the atomic report state. The web unit has read-only access and binds to host loopback port 18450. Its HTTP interface is separate from the case API and demo storage.

The timer checks twice per day at 03:15 and 15:15 EAT, plus an initial activation check. It scans a 30-day catalog window and inspects up to three acquisition days. A selected day must contain both expected grids for the same datatake. Unchanged asset identities reuse previous measurements. A changed object is measured in a size-limited read. A full refresh reads up to 48 MiB plus the bounded catalog response and exits on the first failed source read. The unit has a three-minute runtime limit. A failure retains the last valid report. The web process calculates overdue status at request time so a stopped timer cannot freeze the fresh status.

## Operate the site

Visitors enter through HTTPS on the Contabo hostname. Caddy sends the eight exact public paths above to the Python listener on `127.0.0.1:18450`. Its separate authenticated route serves the private preview. The public process reads validated JSON from `/var/lib/forestproof-visibility/source.json` and generates HTML. The refresh timer runs independently. The successful source-check date and satellite acquisition dates describe different events. The explorer uses a small same-origin script, native buttons and accessible selection states. Without JavaScript, the full dated archive remains open. The Earth is a credited historical NASA composite used for geographic orientation.

The visibility server whitelists the three assets and sends content hashes as ETags. Browsers revalidate assets across releases. Its content policy permits the same-origin script and images. No provider credential or source receipt is delivered to the browser.

Run these read-only commands in your existing Contabo SSH session. Check both browser pages as an anonymous visitor after a release.

```sh
systemctl status forestproof-visibility.service --no-pager
systemctl list-timers forestproof-visibility-refresh.timer --all
journalctl -u forestproof-visibility-refresh.service -n 12 --no-pager
readlink -f /opt/forestproof-visibility/current
```

GitHub holds source and changes. Contabo serves the installed release. Deploy reviewed commits into a new release directory, validate both loopback pages, and retain the old release and gateway config. Switch `current` and restart only the visibility web service. Change the Caddy matcher when public paths change. Keep code, source-report state, and proxy configuration backups separate so a code rollback preserves recent source data.

The separate protected Next.js app uses the root-context `apps/web/Dockerfile` so it can compile the same canonical CSS tokens. Its web container listens on `127.0.0.1:13000`. A web-only release must preserve the existing API container, named demo data volume and gateway. Read the newest release entry in `execution/CURRENT_STATUS.md` before composing a deployment. Retain the original Compose files and apply a reviewed web-image override with `up -d --no-deps --no-build web`. Never substitute a new database or recreate the API as part of a design-only release.

A custom domain points at Contabo through DNS and needs matching Caddy and application host configuration. Verify the certificate and anonymous route boundaries on that hostname before sharing it.

## Gateway and verification

Confirm the exact installed gateway, loopback listener, original auth and bind mount. First verify the live worker and check that the state and case paths return 404 at the loopback listener. Insert [the public matcher](public-route.caddy) ahead of the existing authentication in the explicit Caddy `route` block, preserving all fallback directives. Validate the candidate in the installed Caddy container and retain a root-private copy of the previous config. Use the existing gateway's supported reload procedure. The installed gateway disables the admin API. A supported signal reload requires a file-based start without `--resume` or prior API configuration. [Caddy command and signal documentation](https://caddyserver.com/docs/command-line#signals)

Verify both public URLs over certificate-validated TLS, with GET and HEAD returning the page and writes returning 405. Verify anonymous requests to the existing preview, API and private report still require authentication. Confirm SSH and xrdp are active, the listener remains loopback-only, and the timer has actually executed. Verify the failure and expiry states with isolated test data. If a release check fails, restore the saved gateway configuration and apply it through the same procedure. Leave its existing application containers and database intact.
