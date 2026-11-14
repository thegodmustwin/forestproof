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
const GATEWAY_TOKEN = "G".repeat(43);
const SUBJECT = "pilot-owner-a";
const edgeHeaders = { "X-Forestproof-Owner-Gateway-Token": GATEWAY_TOKEN, "X-Forestproof-Owner-Subject": SUBJECT };
const ENV_KEYS = ["FORESTPROOF_OWNER_GATEWAY_TOKEN", "FORESTPROOF_OWNER_SUBJECT", "FORESTPROOF_API_MODE", "FORESTPROOF_API_INTERNAL_BASE_URL", "FORESTPROOF_INTERNAL_API_TOKEN", "FORESTPROOF_OWNER_GATEWAY_ORIGIN"];

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

function fromGateway(headers = {}) {
  return incoming({ ...edgeHeaders, ...headers });
}
const context = { params: Promise.resolve({ path: ["observations"] }) };

test("owner-demo proxy discards browser-supplied identity headers and uses its server credential", async (t) => {
  restoreEnvironment(t);
  process.env.FORESTPROOF_API_MODE = "owner_demo";
  process.env.FORESTPROOF_OWNER_GATEWAY_TOKEN = GATEWAY_TOKEN;
  process.env.FORESTPROOF_OWNER_SUBJECT = SUBJECT;
  process.env.FORESTPROOF_OWNER_GATEWAY_ORIGIN = "http://127.0.0.1:3000";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = "http://127.0.0.1:8000/api/v1";
  let captured;
  global.fetch = async (url, options) => {
    captured = { url, options };
    return Response.json({ status: "synthetic" });
  };
  const response = await route.GET(fromGateway({ "X-Forestproof-Internal-Token": "B".repeat(43),
    "X-Forestproof-Require-Owner-Demo": "0", "X-Organization-ID": "forged" }), context);
  assert.equal(response.status, 200);
  assert.equal(captured.url, "http://127.0.0.1:8000/api/v1/observations");
  assert.equal(captured.options.headers.get("X-Forestproof-Internal-Token"), TOKEN);
  assert.equal(captured.options.headers.get("X-Forestproof-Require-Owner-Demo"), "1");
  assert.equal(captured.options.headers.get("X-Organization-ID"), null);
  assert.equal(captured.options.headers.get("X-Forestproof-Owner-Subject"), SUBJECT);
  assert.equal(captured.options.headers.get("X-Forestproof-Owner-Gateway-Token"), null);
  assert.equal(response.headers.get("cache-control"), "no-store");
  assert.equal(captured.options.redirect, "error");
  assert.ok(!(await response.text()).includes(TOKEN));
});

test("misconfigured owner-demo proxy does not contact a remote upstream", async (t) => {
  restoreEnvironment(t);
  process.env.FORESTPROOF_API_MODE = "owner_demo";
  process.env.FORESTPROOF_OWNER_GATEWAY_TOKEN = GATEWAY_TOKEN;
  process.env.FORESTPROOF_OWNER_SUBJECT = SUBJECT;
  process.env.FORESTPROOF_OWNER_GATEWAY_ORIGIN = "http://127.0.0.1:3000";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = "https://example.org/api/v1";
  let called = false;
  global.fetch = async () => { called = true; return new Response(); };
  const response = await route.GET(incoming(), context);
  assert.equal(response.status, 503);
  assert.equal(called, false);
  assert.ok(!(await response.text()).includes(TOKEN));
});

test("owner-demo proxy rejects an unverified identity before contacting the API", async (t) => {
  restoreEnvironment(t);
  process.env.FORESTPROOF_API_MODE = "owner_demo";
  process.env.FORESTPROOF_OWNER_GATEWAY_TOKEN = GATEWAY_TOKEN;
  process.env.FORESTPROOF_OWNER_SUBJECT = SUBJECT;
  process.env.FORESTPROOF_OWNER_GATEWAY_ORIGIN = "http://127.0.0.1:3000";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = "http://127.0.0.1:8000/api/v1";
  let called = false;
  global.fetch = async () => { called = true; return new Response(); };
  for (const headers of [{}, { "X-Forestproof-Owner-Subject": SUBJECT },
    { ...edgeHeaders, "X-Forestproof-Owner-Gateway-Token": "B".repeat(43) },
    { ...edgeHeaders, "X-Forestproof-Owner-Subject": "other-owner" },
    { ...edgeHeaders, "X-Forestproof-Owner-Subject": SUBJECT + ", other-owner" }]) {
    const response = await route.GET(incoming(headers), context);
    assert.equal(response.status, 401);
    const body = await response.text();
    assert.ok(!body.includes(TOKEN) && !body.includes(GATEWAY_TOKEN));
  }
  assert.equal(called, false);
});

test("owner-demo proxy rejects dot segments before forwarding any credential", async (t) => {
  restoreEnvironment(t);
  process.env.FORESTPROOF_API_MODE = "owner_demo";
  process.env.FORESTPROOF_OWNER_GATEWAY_TOKEN = GATEWAY_TOKEN;
  process.env.FORESTPROOF_OWNER_SUBJECT = SUBJECT;
  process.env.FORESTPROOF_OWNER_GATEWAY_ORIGIN = "http://127.0.0.1:3000";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = "http://127.0.0.1:8000/api/v1";
  let called = false;
  global.fetch = async () => { called = true; return new Response(); };
  for (const path of [["..", "cases"], ["."], ["cases", ".."]]) {
    const response = await route.GET(fromGateway(), { params: Promise.resolve({ path }) });
    assert.equal(response.status, 400);
    assert.ok(!(await response.text()).includes(TOKEN));
  }
  assert.equal(called, false);
});

test("owner-demo proxy denies unsafe requests without the configured exact Origin", async (t) => {
  restoreEnvironment(t);
  process.env.FORESTPROOF_API_MODE = "owner_demo";
  process.env.FORESTPROOF_OWNER_GATEWAY_TOKEN = GATEWAY_TOKEN;
  process.env.FORESTPROOF_OWNER_SUBJECT = SUBJECT;
  process.env.FORESTPROOF_OWNER_GATEWAY_ORIGIN = "http://127.0.0.1:3000";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = "http://127.0.0.1:8000/api/v1";
  let forwarded = 0;
  global.fetch = async (_url, options) => {
    forwarded += 1;
    assert.equal(options.headers.get("X-Forestproof-Internal-Token"), TOKEN);
    return Response.json({ ok: true }, { status: 201 });
  };
  const post = (origin) => new Request("http://127.0.0.1:3000/api/forestproof/cases", {
    method: "POST", headers: { ...edgeHeaders, ...(origin ? { Origin: origin } : {}), "Content-Type": "application/json" },
    body: "{}",
  });
  const cases = { params: Promise.resolve({ path: ["cases"] }) };
  for (const origin of [undefined, "https://untrusted.example", "http://127.0.0.1:3001"]) {
    const response = await route.POST(post(origin), cases);
    assert.equal(response.status, 403);
    assert.ok(!(await response.text()).includes(TOKEN));
  }
  assert.equal(forwarded, 0);
  assert.equal((await route.POST(post("http://127.0.0.1:3000"), cases)).status, 201);
  assert.equal(forwarded, 1);
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
  assert.equal(sentHeaders.get("X-Forestproof-Owner-Subject"), null);
  assert.equal(sentHeaders.get("X-Forestproof-Owner-Gateway-Token"), null);
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
  process.env.FORESTPROOF_OWNER_GATEWAY_TOKEN = GATEWAY_TOKEN;
  process.env.FORESTPROOF_OWNER_SUBJECT = SUBJECT;
  process.env.FORESTPROOF_OWNER_GATEWAY_ORIGIN = "http://127.0.0.1:3000";
  process.env.FORESTPROOF_INTERNAL_API_TOKEN = TOKEN;
  process.env.FORESTPROOF_API_INTERNAL_BASE_URL = `http://127.0.0.1:${upstream.address().port}/api/v1`;
  try {
    const response = await route.GET(fromGateway(), context);
    assert.equal(response.status, 502);
    assert.equal(targetHits, 0);
    assert.ok(!(await response.text()).includes(TOKEN));
  } finally {
    await Promise.all([new Promise((resolve) => upstream.close(resolve)), new Promise((resolve) => target.close(resolve))]);
  }
});
