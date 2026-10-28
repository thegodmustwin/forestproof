const assert = require("node:assert/strict");
const fs = require("node:fs");
const Module = require("node:module");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");

const filename = path.join(__dirname, "../src/lib/demo.ts");
const js = ts.transpileModule(fs.readFileSync(filename, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const compiled = new Module(filename, module);
compiled.filename = filename;
compiled.paths = module.paths;
compiled._compile(js, filename);
const { findDemoCase } = compiled.exports;

test("a known demo case resolves to its own linked observation", () => {
  const result = findDemoCase("DEMO-CASE-0017");
  assert.equal(result.record.id, "DEMO-CASE-0017");
  assert.equal(result.observation.id, result.record.observationId);
});

test("a missing case never falls back to an unrelated demo case", () => {
  assert.equal(findDemoCase("not-a-real-case"), null);
  assert.equal(findDemoCase(""), null);
});
