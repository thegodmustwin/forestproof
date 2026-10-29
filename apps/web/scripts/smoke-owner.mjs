import assert from "node:assert/strict";
import { execFile, spawn } from "node:child_process";
import { randomBytes } from "node:crypto";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { promisify } from "node:util";

// Isolated synthetic integration: no VPS, provider or real secret.
// Set FORESTPROOF_SMOKE_CADDY to additionally exercise the owner gateway.
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
  if (caddyPath) {
    const password = randomBytes(24).toString("base64url");
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
  console.log(caddyPath ? "Owner gateway and web/API boundary smoke passed with synthetic data and loopback services."
    : "Owner-demo web/API boundary smoke passed with synthetic data and loopback services; gateway authentication was not exercised.");
  console.log("VPS deployment and live ingestion were not exercised.");
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
