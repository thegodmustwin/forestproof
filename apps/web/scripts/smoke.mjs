import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { join } from "node:path";
import { setTimeout as delay } from "node:timers/promises";

// A loopback-only fake API validates the production Next.js proxy without
// contacting a provider or starting the mutable demo API.
const upstream = createServer((request, response) => {
  const chunks = [];
  request.on("data", (chunk) => chunks.push(chunk));
  request.on("end", () => {
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({
      method: request.method,
      url: request.url,
      body: Buffer.concat(chunks).toString("utf8"),
    }));
  });
});
await new Promise((resolve) => upstream.listen(0, "127.0.0.1", resolve));

const reservation = createServer();
await new Promise((resolve) => reservation.listen(0, "127.0.0.1", resolve));
const webPort = reservation.address().port;
await new Promise((resolve, reject) => reservation.close((error) => error ? reject(error) : resolve()));

const next = spawn(process.execPath, [
  join(process.cwd(), "node_modules", "next", "dist", "bin", "next"),
  "start", "-H", "127.0.0.1", "-p", String(webPort),
], {
  env: {
    ...process.env,
    NODE_ENV: "production",
    FORESTPROOF_API_INTERNAL_BASE_URL: "http://127.0.0.1:" + upstream.address().port + "/api/v1",
  },
  stdio: ["ignore", "pipe", "pipe"],
});
let serverLog = "";
next.stdout.on("data", (chunk) => { serverLog += chunk.toString(); });
next.stderr.on("data", (chunk) => { serverLog += chunk.toString(); });
const base = "http://127.0.0.1:" + webPort;

try {
  let ready = false;
  for (let attempt = 0; attempt < 60; attempt += 1) {
    if (next.exitCode !== null) throw new Error("Next.js exited during startup");
    try {
      const response = await fetch(base, { signal: AbortSignal.timeout(1000) });
      if (response.ok) { ready = true; break; }
    } catch {
      // The server may still be starting.
    }
    await delay(500);
  }
  assert.ok(ready, "Next.js did not become ready");

  const getResponse = await fetch(base + "/api/forestproof/health?probe=1");
  assert.equal(getResponse.status, 200);
  assert.deepEqual(await getResponse.json(), { method: "GET", url: "/api/v1/health?probe=1", body: "" });

  const body = JSON.stringify({ observation_id: "synthetic-smoke-test" });
  const postResponse = await fetch(base + "/api/forestproof/cases", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body,
  });
  assert.equal(postResponse.status, 200);
  assert.deepEqual(await postResponse.json(), { method: "POST", url: "/api/v1/cases", body });

  const casePage = await fetch(base + "/cases/synthetic-smoke-test");
  assert.equal(casePage.status, 200);
  assert.match(casePage.headers.get("content-type") ?? "", /text\/html/);
  assert.match(await casePage.text(), /ForestProof/i);
  console.log("Production web smoke checks passed (loopback fake API).");
} catch (error) {
  console.error(serverLog);
  throw error;
} finally {
  next.kill();
  await new Promise((resolve) => upstream.close(resolve));
}
