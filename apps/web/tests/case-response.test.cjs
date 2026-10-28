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
const { loadCaseRecord } = loadTs("../src/lib/api.ts", { "@/lib/observation-normalization": normalizer });

test("case API rejects a different or missing identity and accepts the requested case", async (t) => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  const observation = { id: "demo-observation", quality_flags: ["DEMO_DATA"], geometry: { type: "Point", coordinates: [36.75, -0.38] } };
  global.fetch = async () => Response.json({ id: "different-case", observation });
  await assert.rejects(loadCaseRecord("requested-case"), /requested case/);
  global.fetch = async () => Response.json({ observation });
  await assert.rejects(loadCaseRecord("requested-case"), /requested case/);
  global.fetch = async () => Response.json({ id: "requested-case", observation });
  const result = await loadCaseRecord("requested-case");
  assert.equal(result.record.id, "requested-case");
  assert.equal(result.observation.id, "demo-observation");
});
