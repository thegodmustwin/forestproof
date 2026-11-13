const assert = require("node:assert/strict");
const fs = require("node:fs");
const Module = require("node:module");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");

const filename = path.join(__dirname, "../src/lib/internal-api-config.ts");
const js = ts.transpileModule(fs.readFileSync(filename, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const compiled = new Module(filename, module);
compiled.filename = filename;
compiled.paths = module.paths;
compiled._compile(js, filename);
const { internalApiConfig } = compiled.exports;
const token = "A".repeat(43); // synthetic, never used on a deployed service
const ownerOrigin = "http://127.0.0.1:18080";

test("owner demo forwards its configured secret only to an explicit loopback API", () => {
  assert.deepEqual(internalApiConfig({ FORESTPROOF_API_MODE: "owner_demo", FORESTPROOF_INTERNAL_API_TOKEN: token,
    FORESTPROOF_API_INTERNAL_BASE_URL: "http://127.0.0.1:8000/api/v1/", FORESTPROOF_OWNER_GATEWAY_ORIGIN: ownerOrigin }),
    { base: "http://127.0.0.1:8000/api/v1", ownerDemoToken: token, ownerOrigin });
  assert.equal(internalApiConfig({ FORESTPROOF_API_MODE: "owner_demo", FORESTPROOF_INTERNAL_API_TOKEN: token,
    FORESTPROOF_API_INTERNAL_BASE_URL: "http://[::1]:8000/api/v1", FORESTPROOF_OWNER_GATEWAY_ORIGIN: ownerOrigin }).ownerDemoToken, token);
});

test("owner demo fails closed for malformed or missing secrets and non-loopback upstreams", () => {
  for (const env of [
    { FORESTPROOF_API_INTERNAL_BASE_URL: "http://api:8000/api/v1", FORESTPROOF_INTERNAL_API_TOKEN: token },
    { FORESTPROOF_API_INTERNAL_BASE_URL: "http://example.com/api/v1", FORESTPROOF_INTERNAL_API_TOKEN: token },
    { FORESTPROOF_API_INTERNAL_BASE_URL: "http://localhost:8000/api/v1", FORESTPROOF_INTERNAL_API_TOKEN: token },
    { FORESTPROOF_API_INTERNAL_BASE_URL: "http://user:pass@127.0.0.1:8000/api/v1", FORESTPROOF_INTERNAL_API_TOKEN: token },
    { FORESTPROOF_API_INTERNAL_BASE_URL: "http://127.0.0.1:8000/api/v1?token=x", FORESTPROOF_INTERNAL_API_TOKEN: token },
    { FORESTPROOF_API_INTERNAL_BASE_URL: "http://127.0.0.1:8000/api/v1", FORESTPROOF_INTERNAL_API_TOKEN: "short" },
    { FORESTPROOF_API_INTERNAL_BASE_URL: "http://127.0.0.1:8000/api/v1", FORESTPROOF_INTERNAL_API_TOKEN: `${token}\n` },
    { FORESTPROOF_API_INTERNAL_BASE_URL: "http://127.0.0.1:8000/api/v1" },
  ]) assert.equal(internalApiConfig({ FORESTPROOF_OWNER_GATEWAY_ORIGIN: ownerOrigin, ...env, FORESTPROOF_API_MODE: "owner_demo" }), null);
});

test("owner demo requires an exact IPv4 loopback gateway origin", () => {
  for (const origin of [undefined, "", "http://localhost:18080", "http://[::1]:18080",
    "https://127.0.0.1:18080", "http://127.0.0.1", "http://127.0.0.1:18080/",
    "http://127.0.0.1:18080/path", "http://127.0.0.1:18080?x=1",
    "http://user:pass@127.0.0.1:18080", "http://127.0.0.1:18080.evil.example"]) {
    assert.equal(internalApiConfig({ FORESTPROOF_API_MODE: "owner_demo",
      FORESTPROOF_API_INTERNAL_BASE_URL: "http://127.0.0.1:8000/api/v1",
      FORESTPROOF_INTERNAL_API_TOKEN: token, FORESTPROOF_OWNER_GATEWAY_ORIGIN: origin }), null);
  }
});

test("demo mode never forwards the secret; unknown and live modes fail closed", () => {
  const env = { FORESTPROOF_API_INTERNAL_BASE_URL: "http://api:8000/api/v1", FORESTPROOF_INTERNAL_API_TOKEN: token };
  assert.deepEqual(internalApiConfig(env), { base: "http://api:8000/api/v1" });
  assert.equal(internalApiConfig({ ...env, FORESTPROOF_API_MODE: "live" }), null);
  assert.equal(internalApiConfig({ ...env, FORESTPROOF_API_MODE: "typo" }), null);
});
