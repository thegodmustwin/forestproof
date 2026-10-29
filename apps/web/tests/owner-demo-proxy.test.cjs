const assert = require("node:assert/strict");
const fs = require("node:fs");
const { createServer } = require("node:http");
const Module = require("node:module");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");

function loadTs(filename, dependencies = {}) {
  const absolute = path.join(__dirname, filename);
  const js = ts.transpileModule(fs.readFileSync(absolute, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
  const compiled = new Module(absolute, module);
  compiled.filename = absolute;
  compiled.paths = module.paths;
  const originalRequire = compiled.require.bind(compiled);
  compiled.require = (name) => name in dependencies ? dependencies[name] : originalRequire(name);
  compiled._compile(js, absolute);
  return compiled.exports;
}

class MockNextResponse extends Response {
  static json(value, options) { return Response.json(value, options); }
}

const config = loadTs("../src/lib/internal-api-config.ts");
const route = loadTs("../src/app/api/forestproof/[...path]/route.ts", {
  "next/server": { NextResponse: MockNextResponse },
  "@/lib/internal-api-config": config,
});
const TOKEN = "A".repeat(43); // synthetic test fixture; never used for deployment
const ENV_KEYS = ["FORESTPROOF_API_MODE", "FORESTPROOF_API_INTERNAL_BASE_URL", "FORESTPROOF_INTERNAL_API_TOKEN"];

function restoreEnvironment(t) {
  const old = Object.fromEntries(ENV_KEYS.map((key) => [key, process.env[key]]));
  const oldFetch = global.fetch;
  t.after(() => {
    for (const key of ENV_KEYS) {
      if (old[key] === undefined) delete process.env[key]; else process.env[key] = old[key];
    }
    global.fetch = oldFetch;
  });
}

function incoming(headers = {}) {
  return new Request("http://127.0.0.1:3000/api/forestproof/observations", { headers });
}
const context = { params: Promise.resolve({ path: ["observations"] }) };

test("owner-demo proxy discards browser-supplied identity headers and uses its server credential", async (t) => {
  restoreEnvironment(t);
  process.env.FORESTPROOF_API_MODE = "owner_demo";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = "http://127.0.0.1:8000/api/v1";
  let captured;
  global.fetch = async (url, options) => {
    captured = { url, options };
    return Response.json({ status: "synthetic" });
  };
  const response = await route.GET(incoming({ "X-Forestproof-Internal-Token": "B".repeat(43),
    "X-Forestproof-Require-Owner-Demo": "0", "X-Organization-ID": "forged" }), context);
  assert.equal(response.status, 200);
  assert.equal(captured.url, "http://127.0.0.1:8000/api/v1/observations");
  assert.equal(captured.options.headers.get("X-Forestproof-Internal-Token"), TOKEN);
  assert.equal(captured.options.headers.get("X-Forestproof-Require-Owner-Demo"), "1");
  assert.equal(captured.options.headers.get("X-Organization-ID"), null);
  assert.equal(captured.options.redirect, "error");
  assert.ok(!(await response.text()).includes(TOKEN));
});

test("misconfigured owner-demo proxy does not contact a remote upstream", async (t) => {
  restoreEnvironment(t);
  process.env.FORESTPROOF_API_MODE = "owner_demo";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = "https://example.org/api/v1";
  let called = false;
  global.fetch = async () => { called = true; return new Response(); };
  const response = await route.GET(incoming(), context);
  assert.equal(response.status, 503);
  assert.equal(called, false);
  assert.ok(!(await response.text()).includes(TOKEN));
});

test("owner-demo proxy rejects dot segments before forwarding any credential", async (t) => {
  restoreEnvironment(t);
  process.env.FORESTPROOF_API_MODE = "owner_demo";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = "http://127.0.0.1:8000/api/v1";
  let called = false;
  global.fetch = async () => { called = true; return new Response(); };
  for (const path of [["..", "cases"], ["."], ["cases", ".."]]) {
    const response = await route.GET(incoming(), { params: Promise.resolve({ path }) });
    assert.equal(response.status, 400);
    assert.ok(!(await response.text()).includes(TOKEN));
  }
  assert.equal(called, false);
});

test("demo proxy does not pass the configured service token or client-spoofed token", async (t) => {
  restoreEnvironment(t);
  process.env.FORESTPROOF_API_MODE = "demo";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = "http://api:8000/api/v1";
  let sentHeaders;
  global.fetch = async (_url, options) => { sentHeaders = options.headers; return Response.json({ ok: true }); };
  assert.equal((await route.GET(incoming({ "X-Forestproof-Internal-Token": "forged" }), context)).status, 200);
  assert.equal(sentHeaders.get("X-Forestproof-Internal-Token"), null);
  assert.equal(sentHeaders.get("X-Forestproof-Require-Owner-Demo"), null);
});

test("real fetch refuses redirects without forwarding the service token to the target", async (t) => {
  restoreEnvironment(t);
  let targetHits = 0;
  const target = createServer((_request, response) => { targetHits += 1; response.end("unexpected"); });
  await new Promise((resolve) => target.listen(0, "127.0.0.1", resolve));
  const upstream = createServer((_request, response) => {
    response.writeHead(302, { Location: `http://127.0.0.1:${target.address().port}/` });
    response.end();
  });
  await new Promise((resolve) => upstream.listen(0, "127.0.0.1", resolve));
  process.env.FORESTPROOF_API_MODE = "owner_demo";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = `http://127.0.0.1:${upstream.address().port}/api/v1`;
  try {
    const response = await route.GET(incoming(), context);
    assert.equal(response.status, 502);
    assert.equal(targetHits, 0);
    assert.ok(!(await response.text()).includes(TOKEN));
  } finally {
    await Promise.all([new Promise((resolve) => upstream.close(resolve)), new Promise((resolve) => target.close(resolve))]);
  }
});
