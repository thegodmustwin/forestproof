import { copyFile, mkdir, stat } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// Serve the worker belonging to the installed, locked MapLibre dependency.
// Its default adjacent-module URL is relocated by the application bundler.
const distribution = dirname(fileURLToPath(import.meta.resolve("maplibre-gl")));
const destination = resolve(dirname(fileURLToPath(import.meta.url)), "../public/vendor");
const worker = join(distribution, "maplibre-gl-worker.mjs");
const size = (await stat(worker)).size;
if (size === 0 || size > 2 * 1024 * 1024) throw new Error("Unexpected MapLibre worker artifact");
await mkdir(destination, { recursive: true });
await copyFile(worker, join(destination, "maplibre-gl-worker.mjs"));
await copyFile(resolve(distribution, "../LICENSE.txt"), join(destination, "maplibre-LICENSE.txt"));
console.log("Prepared the installed MapLibre worker and licence for same-origin serving.");
