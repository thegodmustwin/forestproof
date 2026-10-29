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
const { loadCopernicusSceneContext } = loadTs("../src/lib/api.ts", { "@/lib/observation-normalization": normalizer });
const base = { collection: "sentinel-2-l2a", checked_at: "2026-10-29T13:00:00Z",
  scenes: [{ id: "S2_SYNTHETIC", acquired_at: "2026-10-28T08:00:00Z", platform: "sentinel-2a", scene_cloud_cover_percent: 0 }] };

test("scene lookup preserves genuine zero cloud cover and supports an empty sample", async (t) => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  global.fetch = async () => Response.json(base);
  const result = await loadCopernicusSceneContext();
  assert.equal(result.scenes[0].sceneCloudCoverPercent, 0);
  assert.equal(result.scenes[0].id, "S2_SYNTHETIC");
  global.fetch = async () => Response.json({ ...base, scenes: [] });
  assert.deepEqual((await loadCopernicusSceneContext()).scenes, []);
});

test("scene lookup rejects unavailable, malformed and unsupported metadata", async (t) => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  for (const payload of [
    { ...base, collection: "other" }, { ...base, checked_at: "not-a-date" },
    { ...base, scenes: [{ ...base.scenes[0], scene_cloud_cover_percent: 101 }] },
    { ...base, scenes: [{ ...base.scenes[0], acquired_at: "not-a-date" }] },
    { ...base, scenes: [{ ...base.scenes[0], id: "" }] },
    { ...base, scenes: Array(4).fill(base.scenes[0]) },
  ]) {
    global.fetch = async () => Response.json(payload);
    await assert.rejects(loadCopernicusSceneContext());
  }
  global.fetch = async () => new Response("unavailable", { status: 503 });
  await assert.rejects(loadCopernicusSceneContext(), /unavailable/);
});
