const assert = require("node:assert/strict");
const fs = require("node:fs");
const Module = require("node:module");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");

function createHarness() {
  const slots = [];
  const dependencies = [];
  const cleanups = [];
  const effects = [];
  const maps = [];
  const workerUrls = [];
  let cursor = 0;
  const react = {
    useRef(initial) {
      const index = cursor++;
      slots[index] ??= { current: index === 0 ? {} : initial };
      return slots[index];
    },
    useState(initial) {
      const index = cursor++;
      if (!(index in slots)) slots[index] = initial;
      return [slots[index], (value) => { slots[index] = typeof value === "function" ? value(slots[index]) : value; }];
    },
    useEffect(effect, deps) {
      const index = cursor++;
      const previous = dependencies[index];
      if (!previous || deps.some((value, offset) => !Object.is(value, previous[offset]))) {
        effects.push(() => {
          cleanups[index]?.();
          cleanups[index] = effect();
          dependencies[index] = deps;
        });
      }
    },
  };
  class MapMock {
    constructor() { this.handlers = {}; this.removed = 0; maps.push(this); }
    on(name, handler) { this.handlers[name] = handler; }
    addControl() {}
    resize() {}
    remove() { this.removed += 1; }
  }
  class MarkerMock {
    constructor({ element }) { this.element = element; this.removed = false; }
    setLngLat(position) { this.position = position; return this; }
    addTo(map) { (map.markers ??= []).push(this); return this; }
    getElement() { return this.element; }
    remove() { this.removed = true; }
  }
  const jsx = (type, props) => ({ type, props });
  const filename = path.join(__dirname, "../src/components/aberdare-map.tsx");
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX },
  }).outputText;
  const loaded = new Module(filename, module);
  loaded.filename = filename;
  loaded.paths = module.paths;
  loaded.require = (name) => {
    if (name === "react") return react;
    if (name === "react/jsx-runtime") return { jsx, jsxs: jsx };
    if (name === "maplibre-gl") return {
      Map: MapMock, Marker: MarkerMock, NavigationControl: class {},
      setWorkerUrl: (url) => workerUrls.push(url),
    };
    if (name === "@/lib/demo") return { monitoredArea: { center: [36.74, -0.38] }, observations: [] };
    return require(name);
  };
  loaded._compile(output, filename);
  return {
    maps,
    workerUrls,
    render(props) {
      cursor = 0;
      const tree = loaded.exports.AberdareMap(props);
      while (effects.length) effects.shift()();
      return tree;
    },
    dispose() { cleanups.forEach((cleanup) => cleanup?.()); },
  };
}

function visibleText(node) {
  if (node == null || typeof node === "boolean") return "";
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(visibleText).join(" ");
  return visibleText(node.props?.children);
}

test("style readiness enables markers before imagery finishes and later selection updates preserve the map", () => {
  const previousDocument = global.document;
  global.document = {
    createElement() {
      return {
        handlers: {}, attributes: {},
        addEventListener(name, callback) { this.handlers[name] = callback; },
        setAttribute(name, value) { this.attributes[name] = value; },
      };
    },
  };
  const harness = createHarness();
  try {
    const records = [{ id: "DEMO-A", title: "First", coordinates: [36.7, -0.4] }];
    let picked = null;
    harness.render({ selectedId: "", observations: records, onSelect: () => { throw new Error("stale callback"); } });
    assert.equal(harness.maps.length, 1);
    assert.deepEqual(harness.workerUrls, ["/vendor/maplibre-gl-worker.mjs"]);
    const map = harness.maps[0];
    map.handlers["style.load"]();
    let tree = harness.render({ selectedId: "", observations: records, onSelect: () => { throw new Error("stale callback"); } });
    assert.match(visibleText(tree), /Loading base map imagery/);
    assert.match(visibleText(tree), /Explore 3D terrain/);
    const marker = map.markers[0];
    assert.ok(marker, "Markers should be available while base imagery is loading");
    map.handlers.load();
    tree = harness.render({ selectedId: "", observations: records, onSelect: () => {} });
    assert.doesNotMatch(visibleText(tree), /Loading base map imagery/);
    const revised = [{ ...records[0], title: "Revised", coordinates: [36.8, -0.3] }];
    harness.render({ selectedId: "DEMO-A", observations: revised, onSelect: (record) => { picked = record; } });
    assert.equal(harness.maps.length, 1);
    assert.equal(harness.workerUrls.length, 1);
    assert.equal(map.markers.length, 1);
    assert.equal(marker.element.attributes["aria-pressed"], "true");
    assert.deepEqual(marker.position, [36.8, -0.3]);
    marker.element.handlers.click();
    assert.equal(picked, revised[0]);
    harness.render({ selectedId: "", observations: [], onSelect: () => {} });
    assert.equal(marker.removed, true);
    harness.dispose();
    assert.equal(map.removed, 1);
  } finally {
    global.document = previousDocument;
  }
});
