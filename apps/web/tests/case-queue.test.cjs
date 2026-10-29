const assert = require("node:assert/strict");
const fs = require("node:fs");
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

const normalizer = loadTs("../src/lib/observation-normalization.ts");
const { loadCaseQueue } = loadTs("../src/lib/api.ts", { "@/lib/observation-normalization": normalizer });
const fixture = { id: "saved-case", title: "Synthetic review", status: "UNDER_REVIEW", observation_id: "demo-observation",
  observation_classification: "REQUIRES_HUMAN_REVIEW", owner_organization: "Demo team", created_at: "2026-10-29T08:00:00Z", quality_flags: ["DEMO_DATA"] };

test("the case queue shows saved API records and treats an empty queue as empty", async (t) => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  global.fetch = async () => Response.json({ items: [fixture] });
  const results = await loadCaseQueue();
  assert.equal(results.length, 1);
  assert.deepEqual(results[0], { id: "saved-case", title: "Synthetic review", status: "UNDER_REVIEW", owner: "Demo team",
    observationId: "demo-observation", observationClassification: "REQUIRES_HUMAN_REVIEW", openedAt: "2026-10-29T08:00:00Z" });
  global.fetch = async () => Response.json({ items: [] });
  assert.deepEqual(await loadCaseQueue(), []);
});

test("the queue refuses unlabelled, malformed or unknown-state records instead of inventing a case", async (t) => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  for (const bad of [
    { ...fixture, quality_flags: [] }, { ...fixture, id: "" }, { ...fixture, observation_id: undefined },
    { ...fixture, status: "NOT_A_REAL_STATE" }, null,
  ]) {
    global.fetch = async () => Response.json({ items: [bad] });
    await assert.rejects(loadCaseQueue());
  }
  global.fetch = async () => Response.json({ items: "not a list" });
  await assert.rejects(loadCaseQueue(), /malformed/);
  global.fetch = async () => new Response("unavailable", { status: 503 });
  await assert.rejects(loadCaseQueue(), /503/);
});
