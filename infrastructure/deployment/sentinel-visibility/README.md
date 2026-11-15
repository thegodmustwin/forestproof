# Contabo Geta visibility release

The approved public surface is `/visibility` on the existing ForestProof HTTPS hostname, with the label **Provisional Geta research area**. It publishes aggregate counts for the two overlapping native Sentinel-2 grids and the Copernicus attribution. The private source receipts stay in the service state directory. Alert and case routes remain under the existing tester gateway.

## Runtime

Use the versioned code under `/opt/forestproof-visibility/current`, an isolated pinned raster environment under `/opt/forestproof-visibility/venv`, and the dedicated unprivileged `forestproof-visibility` account. The units in this folder share `/var/lib/forestproof-visibility` for the atomic report state. The web unit has read-only access and binds to host loopback port 18450. Its HTTP interface is separate from the case API and demo storage.

The timer checks twice per day at 03:15 and 15:15 EAT, plus an initial activation check. It scans a 30-day catalog window and inspects up to three acquisition days. A selected day must contain both expected grids for the same datatake. Unchanged asset identities reuse previous measurements. A changed object is measured in a size-limited read. A full refresh reads up to 48 MiB plus the bounded catalog response and exits on the first failed source read. The unit has a three-minute runtime limit. A failure retains the last valid report. The web process calculates overdue status at request time so a stopped timer cannot freeze the fresh status.

## Gateway and verification

Confirm the exact installed gateway, loopback listener, original auth and bind mount. First verify the live worker and check that the state and case paths return 404 at the loopback listener. Insert [the public matcher](public-route.caddy) ahead of the existing authentication in the explicit Caddy `route` block, preserving all fallback directives. Validate the candidate in the installed Caddy container and retain a root-private copy of the previous config. Use the existing gateway's supported reload procedure. The installed gateway disables the admin API. A supported signal reload requires a file-based start without `--resume` or prior API configuration. [Caddy command and signal documentation](https://caddyserver.com/docs/command-line#signals)

Verify the public URL over certificate-validated TLS, with GET and HEAD returning the page and writes returning 405. Verify anonymous requests to the existing preview, API and private report still require authentication. Confirm SSH and xrdp are active, the listener remains loopback-only, and the timer has actually executed. Verify the failure and expiry states with isolated test data. If a release check fails, restore the saved gateway configuration and apply it through the same procedure. Leave its existing application containers and database intact.
