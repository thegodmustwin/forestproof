import assert from "node:assert/strict";
import { execFile, spawn } from "node:child_process";
import { randomBytes } from "node:crypto";
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { promisify } from "node:util";

// Isolated synthetic integration: no VPS, provider or real secret.
// Set FORESTPROOF_SMOKE_CADDY to additionally exercise the owner gateway.
// FORESTPROOF_SMOKE_REAL_CATALOG=1 explicitly opts into a bounded public
// Copernicus scene-metadata request; it is never enabled by the CI workflow.
async function freePort() {
  const server = createServer();
  await new Promise((resolveListen) => server.listen(0, "127.0.0.1", resolveListen));
  const port = server.address().port;
  await new Promise((resolveClose, reject) => server.close((error) => error ? reject(error) : resolveClose()));
  return port;
}

const temp = await mkdtemp(join(tmpdir(), "forestproof-owner-smoke-"));
const apiPort = await freePort();
let webPort = await freePort();
while (webPort === apiPort) webPort = await freePort();
const caddyPath = process.env.FORESTPROOF_SMOKE_CADDY;
let gatewayPort = caddyPath ? await freePort() : null;
while (gatewayPort !== null && (gatewayPort === webPort || gatewayPort === apiPort)) gatewayPort = await freePort();
const token = randomBytes(32).toString("base64url");
const apiBase = `http://127.0.0.1:${apiPort}`;
const webBase = `http://127.0.0.1:${webPort}`;
const apiDir = resolve(process.cwd(), "../../services/api");
const python = process.env.FORESTPROOF_SMOKE_PYTHON || "python3";
const realCatalog = process.env.FORESTPROOF_SMOKE_REAL_CATALOG === "1";
const children = [];
const syntheticSecrets = [token];
let logs = "";

function start(command, args, options) {
  const child = spawn(command, args, { ...options, stdio: ["ignore", "pipe", "pipe"] });
  child.on("error", () => { child.spawnFailed = true; });
  child.stdout.on("data", (chunk) => { logs += chunk.toString(); });
  child.stderr.on("data", (chunk) => { logs += chunk.toString(); });
  children.push(child);
  return child;
}

async function waitFor(url, child, expectedStatus = 200) {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    if (child.spawnFailed || child.exitCode !== null || child.signalCode !== null) throw new Error("A smoke-test service exited during startup");
    try {
      const response = await fetch(url, { signal: AbortSignal.timeout(1000) });
      if (response.status === expectedStatus) return;
    } catch {
      // Local service may still be starting.
    }
    await delay(500);
  }
  throw new Error("A smoke-test service did not become ready");
}

try {
  const api = start(python, ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", String(apiPort)], {
    cwd: apiDir,
    env: { ...process.env, FORESTPROOF_MODE: "owner_demo", FORESTPROOF_INTERNAL_API_TOKEN: token,
      FORESTPROOF_SQLITE_PATH: join(temp, "demo.sqlite"), EVIDENCE_STORAGE_PATH: join(temp, "evidence"),
      FORESTPROOF_COPERNICUS_CATALOG_ENABLED: realCatalog ? "true" : "false",
      WEB_ORIGIN: gatewayPort === null ? webBase : `http://127.0.0.1:${gatewayPort}` },
  });
  await waitFor(`${apiBase}/api/v1/health`, api);

  const web = start(process.execPath, [join(process.cwd(), "node_modules", "next", "dist", "bin", "next"),
    "start", "-H", "127.0.0.1", "-p", String(webPort)], {
    cwd: process.cwd(),
    env: { ...process.env, NODE_ENV: "production", FORESTPROOF_API_MODE: "owner_demo",
      FORESTPROOF_INTERNAL_API_TOKEN: token, FORESTPROOF_API_INTERNAL_BASE_URL: `${apiBase}/api/v1` },
  });
  await waitFor(webBase, web);

  let entryBase = webBase;
  let authHeaders = {};
  let gatewayPassword;
  if (caddyPath) {
    const password = randomBytes(24).toString("base64url");
    gatewayPassword = password;
    const { stdout } = await promisify(execFile)(caddyPath, ["hash-password", "--plaintext", password]);
    const passwordHash = stdout.trim();
    assert.match(passwordHash, /^\$2[aby]\$/);
    const credentials = `Basic ${Buffer.from(`owner:${password}`).toString("base64")}`;
    syntheticSecrets.push(password, passwordHash, credentials);
    const template = await readFile(resolve(process.cwd(), "../../infrastructure/deployment/owner-pilot/Caddyfile"), "utf8");
    assert.ok(template.includes("{$FORESTPROOF_OWNER_GATEWAY_PORT:INVALID_REQUIRED_PORT}") && template.includes("{$FORESTPROOF_OWNER_WEB_PORT:INVALID_REQUIRED_PORT}"));
    const config = template;
    const configPath = join(temp, "Caddyfile");
    await writeFile(configPath, config, { mode: 0o600 });
    const gateway = start(caddyPath, ["run", "--config", configPath, "--adapter", "caddyfile"], {
      cwd: temp, env: { ...process.env, FORESTPROOF_OWNER_PASSWORD_HASH: passwordHash,
        FORESTPROOF_OWNER_GATEWAY_PORT: String(gatewayPort), FORESTPROOF_OWNER_WEB_PORT: String(webPort) },
    });
    entryBase = `http://127.0.0.1:${gatewayPort}`;
    authHeaders = { Authorization: credentials };
    await waitFor(entryBase, gateway, 401);
    assert.equal((await fetch(`${entryBase}/api/forestproof/observations`)).status, 401);
    assert.equal((await fetch(entryBase, { headers: { Authorization: `Basic ${Buffer.from("owner:incorrect").toString("base64")}` } })).status, 401);
    const crossOrigin = await fetch(`${entryBase}/api/forestproof/cases`, {
      method: "POST", headers: { ...authHeaders, Origin: "https://untrusted.example", "Content-Type": "application/json" },
      body: JSON.stringify({ title: "Synthetic blocked test" }),
    });
    assert.equal(crossOrigin.status, 403);
  }

  assert.equal((await fetch(`${apiBase}/api/v1/observations`)).status, 401);
  assert.equal((await fetch(`${apiBase}/api/v1/observations`, { headers: { "X-Forestproof-Internal-Token": "B".repeat(43) } })).status, 401);
  const preflight = await fetch(`${apiBase}/api/v1/observations`, { method: "OPTIONS", headers: {
    Origin: entryBase, "Access-Control-Request-Method": "GET",
  } });
  assert.equal(preflight.headers.get("Access-Control-Allow-Origin"), entryBase);
  const direct = await fetch(`${apiBase}/api/v1/observations`, { headers: { "X-Forestproof-Internal-Token": token } });
  assert.equal(direct.status, 200);
  const observed = await fetch(`${entryBase}/api/forestproof/observations`, {
    headers: { ...authHeaders, "X-Forestproof-Internal-Token": "B".repeat(43), "X-Forestproof-Require-Owner-Demo": "0" },
  });
  assert.equal(observed.status, 200);
  const observations = await observed.json();
  assert.equal(observations.mode, "OWNER_DEMO");
  assert.ok(observations.items.length > 0 && observations.items.every((item) => item.quality_flags.includes("DEMO_DATA")));
  assert.ok(!JSON.stringify(observations).includes(token));

  const created = await fetch(`${entryBase}/api/forestproof/cases`, {
    method: "POST", headers: { ...authHeaders, Origin: entryBase, "Content-Type": "application/json" },
    body: JSON.stringify({ observation_id: observations.items[0].id, title: "Synthetic owner smoke",
      owner_organization: "Demo team", reviewer: "Untrusted client label" }),
  });
  assert.equal(created.status, 201);
  const caseId = (await created.json()).id;
  const detail = await fetch(`${entryBase}/api/forestproof/cases/${encodeURIComponent(caseId)}`, { headers: authHeaders });
  assert.equal(detail.status, 200);
  const caseRecord = await detail.json();
  assert.equal(caseRecord.events[0].actor, "owner");

  const evidence = await fetch(`${entryBase}/api/forestproof/cases/${encodeURIComponent(caseId)}/evidence`, {
    method: "POST", headers: { ...authHeaders, Origin: entryBase, "Content-Type": "application/json" },
    body: JSON.stringify({ file_name: "demo.txt", content_base64: "dGVzdA==", source_description: "Synthetic", actor: "spoof" }),
  });
  assert.equal(evidence.status, 409);
  const live = await fetch(`${entryBase}/api/forestproof/ingestion/live/gfw`, { method: "POST", headers: { ...authHeaders, Origin: entryBase } });
  assert.equal(live.status, 409);
  assert.equal((await fetch(`${apiBase}/api/v1/context/copernicus-scenes`)).status, 401);
  const sceneResponse = await fetch(`${entryBase}/api/forestproof/context/copernicus-scenes`, { headers: authHeaders });
  assert.equal(sceneResponse.status, realCatalog ? 200 : 503);
  const scenePayload = realCatalog ? await sceneResponse.json() : null;
  if (scenePayload) {
    assert.equal(scenePayload.collection, "sentinel-2-l2a");
    assert.ok(Array.isArray(scenePayload.scenes) && scenePayload.scenes.length <= 3);
    assert.match(scenePayload.notice, /not a forest-loss alert/);
  }

  if (process.env.FORESTPROOF_CHROME_EXECUTABLE) {
    const { chromium } = await import("playwright-core");
    const browser = await chromium.launch({ executablePath: process.env.FORESTPROOF_CHROME_EXECUTABLE, headless: true,
      args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
    try {
      const context = await browser.newContext(gatewayPassword ? { httpCredentials: { username: "owner", password: gatewayPassword } } : {});
      const page = await context.newPage();
      const pageErrors = [];
      page.on("pageerror", (error) => pageErrors.push(error.message));
      const tile = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=", "base64");
      await page.route("**/*", async (route) => {
        const url = route.request().url();
        if (url.startsWith(`${entryBase}/`)) return route.continue();
        if (url.startsWith("https://tile.openstreetmap.org/")) return route.fulfill({ status: 200, contentType: "image/png", body: tile });
        return route.abort();
      });
      await page.goto(`${entryBase}/monitor/aberdare`, { waitUntil: "domcontentloaded" });
      await page.getByText("API connected.", { exact: false }).waitFor();
      assert.equal(await page.getByText("Source record", { exact: true }).count(), 1);
      assert.match(await page.locator(".fact").filter({ hasText: "Coverage completeness" }).innerText(), /Unknown/);
      if (process.env.FORESTPROOF_SCREENSHOT_DIR) {
        const captureDir = resolve(process.env.FORESTPROOF_SCREENSHOT_DIR);
        await mkdir(captureDir, { recursive: true });
        for (const [name, viewport] of [["monitor-desktop", { width: 1440, height: 1100 }], ["monitor-mobile", { width: 390, height: 844 }]]) {
          await page.setViewportSize(viewport);
          await page.screenshot({ path: join(captureDir, `forestproof-${name}.png`), fullPage: true, animations: "disabled" });
          const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
          assert.equal(overflow, false, `Monitoring view overflows ${name}`);
        }
        await page.setViewportSize({ width: 1440, height: 1100 });
      }
      await page.getByRole("button", { name: "Create review case" }).click();
      const openRecord = page.getByRole("link", { name: "Open the review record" });
      await openRecord.waitFor();
      assert.equal(await openRecord.getAttribute("href"), `/cases/${caseId}`);

      if (process.env.FORESTPROOF_SCREENSHOT_DIR) {
        const captureDir = resolve(process.env.FORESTPROOF_SCREENSHOT_DIR);
        await mkdir(captureDir, { recursive: true });
        for (const [name, viewport] of [["desktop", { width: 1440, height: 1100 }], ["mobile", { width: 390, height: 844 }]]) {
          await page.setViewportSize(viewport);
          await page.goto(entryBase, { waitUntil: "networkidle" });
          await page.getByText("Synthetic owner smoke", { exact: true }).waitFor();
          await page.screenshot({ path: join(captureDir, `forestproof-${name}.png`), fullPage: true, animations: "disabled" });
          const overflow = await page.evaluate(() => ({ width: window.innerWidth, scrollWidth: document.documentElement.scrollWidth, offenders: [...document.querySelectorAll("body *")].filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.right > window.innerWidth + 1 && getComputedStyle(el).position !== "absolute"; }).slice(0, 8).map(el => el.className) }));
          assert.ok(overflow.scrollWidth <= overflow.width + 1, `Page overflows the viewport: ${JSON.stringify(overflow)}`);
          const brand = await page.locator(".brand").boundingBox();
          const sidebar = await page.locator(".sidebar").boundingBox();
          assert.ok(brand && sidebar && brand.x + brand.width <= sidebar.x + sidebar.width + 1, "Brand overflows navigation");
        }
        await page.setViewportSize({ width: 1440, height: 1100 });
      }

      await page.goto(`${entryBase}/operations`, { waitUntil: "domcontentloaded" });
      await page.getByText(caseId, { exact: false }).waitFor();
      const queueRow = page.locator("tbody tr").filter({ hasText: caseId });
      assert.equal(await queueRow.count(), 1);
      assert.match(await queueRow.innerText(), /Synthetic owner smoke/);
      await page.goto(`${entryBase}/cases/${caseId}`, { waitUntil: "domcontentloaded" });
      await page.getByRole("button", { name: "Advance to Under review" }).click();
      await page.getByRole("button", { name: "Advance to Field verification" }).click();
      const advanceAction = page.getByRole("button", { name: "Advance to Action recorded" });
      await advanceAction.waitFor();
      assert.equal(await advanceAction.isDisabled(), true);
      await page.getByLabel("What action was taken?").fill("Synthetic request for a review.");
      await page.getByRole("button", { name: "Save demo action" }).click();
      await page.getByText("Synthetic action saved. You can now advance the case.").waitFor();
      await advanceAction.click();
      await page.getByRole("button", { name: "Advance to Follow-up" }).click();
      const close = page.getByRole("button", { name: "Advance to Closed" });
      await close.waitFor();
      assert.equal(await close.isDisabled(), true);
      await page.getByLabel("What did the follow-up find?").fill("Synthetic follow-up remains unresolved.");
      await page.getByRole("button", { name: "Save demo follow-up" }).click();
      await page.getByText("Synthetic follow-up saved. You can now close the case.").waitFor();
      await close.click();
      await page.getByText("Saved: Follow-up → Closed.").waitFor();
      await page.reload({ waitUntil: "domcontentloaded" });
      await page.getByText("Synthetic request for a review.").waitFor();
      await page.getByText("Synthetic follow-up remains unresolved.").waitFor();
      await page.getByRole("link", { name: observations.items[0].id, exact: true }).click();
      await page.locator(".detail-panel").getByText(observations.items[0].id, { exact: true }).waitFor();
      await page.goto(`${entryBase}/monitor/aberdare?observation=${encodeURIComponent(observations.items[1].id)}`, { waitUntil: "domcontentloaded" });
      await page.locator(".detail-panel").getByText(observations.items[1].id, { exact: true }).waitFor();
      assert.equal(await page.locator(".detail-panel").getByText(observations.items[0].id, { exact: true }).count(), 0);
      await page.goto(`${entryBase}/monitor/aberdare?observation=missing-example`, { waitUntil: "domcontentloaded" });
      await page.getByText("Observation unavailable", { exact: true }).waitFor();
      assert.equal(await page.getByRole("button", { name: "Create review case" }).count(), 0);
      await page.goto(`${entryBase}/operations`, { waitUntil: "domcontentloaded" });
      await page.getByText(caseId, { exact: false }).waitFor();
      assert.equal(await page.getByText("Closed", { exact: true }).count(), 1);
      await page.goto(`${entryBase}/`, { waitUntil: "domcontentloaded" });
      await page.getByText("No open demo cases yet.").waitFor();
      await page.goto(`${entryBase}/sources`, { waitUntil: "domcontentloaded" });
      await page.getByRole("button", { name: "Look up recent scenes" }).click();
      if (realCatalog) {
        await page.getByText("Catalog checked", { exact: false }).waitFor();
        if (scenePayload.scenes.length > 0) await page.getByText(scenePayload.scenes[0].id, { exact: true }).waitFor();
      } else await page.getByText("The owner-only scene lookup is disabled or temporarily unavailable.", { exact: false }).waitFor();
      assert.deepEqual(pageErrors, []);
      console.log("Browser workflow passed through the saved demo case, action, follow-up and closure.");
    } finally { await browser.close(); }
  }
  console.log(caddyPath ? "Owner gateway and web/API boundary smoke passed with synthetic data and loopback services."
    : "Owner-demo web/API boundary smoke passed with synthetic data and loopback services; gateway authentication was not exercised.");
  if (realCatalog) console.log("A bounded public Copernicus scene-metadata lookup was also exercised; scenes are not alerts.");
  console.log("VPS deployment and live alert ingestion were not exercised.");
} catch (error) {
  // These are synthetic values; redact them even if a child logs them.
  for (const secret of syntheticSecrets) logs = logs.replaceAll(secret, "[redacted]");
  console.error(logs);
  throw error;
} finally {
  for (const child of children) child.kill("SIGTERM");
  await Promise.all(children.map((child) => new Promise((resolveExit) => {
    if (child.exitCode !== null || child.signalCode !== null) return resolveExit();
    child.once("exit", resolveExit);
    setTimeout(() => { child.kill("SIGKILL"); resolveExit(); }, 3000).unref();
  })));
  await rm(temp, { recursive: true, force: true });
}
