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
    FORESTPROOF_API_MODE: "demo",
    FORESTPROOF_INTERNAL_API_TOKEN: "",
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
  if (process.argv.includes("--browser")) {
    const executablePath = process.env.FORESTPROOF_CHROME_EXECUTABLE;
    if (!executablePath) throw new Error("Set FORESTPROOF_CHROME_EXECUTABLE to a local Chrome or Chromium binary");
    const { chromium } = await import("playwright-core");
    const browser = await chromium.launch({
      executablePath,
      headless: true,
      args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
    });
    try {
      const page = await browser.newPage();
      const pageErrors = [];
      page.on("pageerror", (error) => pageErrors.push(error.message));
      const tile = Buffer.from(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
        "base64",
      );
      await page.route("**/*", async (route) => {
        const url = route.request().url();
        if (url.startsWith(base + "/")) return route.continue();
        if (url.startsWith("https://tile.openstreetmap.org/")) {
          return route.fulfill({ status: 200, contentType: "image/png", body: tile });
        }
        return route.abort();
      });
      await page.goto(base + "/monitor/aberdare", { waitUntil: "domcontentloaded" });
      await page.waitForSelector(".maplibregl-canvas", { timeout: 30000 });
      await page.waitForSelector(".fp-map-marker", { timeout: 30000 });
      const markers = page.locator(".fp-map-marker");
      assert.ok(await markers.count() >= 2, "Synthetic map markers did not render");
      assert.equal(await page.locator(".map-canvas").count(), 0, "Map is still in fallback mode");
      assert.match(await page.locator("body").innerText(), /DEMO/i);
      const selectedLabel = await markers.nth(1).getAttribute("aria-label");
      assert.ok(selectedLabel);
      await markers.nth(1).click();
      await page.waitForFunction(
        (label) => document.querySelector(".fp-map-marker.selected")?.getAttribute("aria-label") === label,
        selectedLabel,
        { timeout: 30000 },
      );
      assert.deepEqual(pageErrors, [], "The map page raised a browser error");
      console.log("Browser map smoke passed with synthetic fixtures and local tiles.");
    } finally {
      await browser.close();
    }
  }
  console.log("Production web smoke checks passed (loopback fake API).");
} catch (error) {
  console.error(serverLog);
  throw error;
} finally {
  next.kill();
  await new Promise((resolve) => upstream.close(resolve));
}
