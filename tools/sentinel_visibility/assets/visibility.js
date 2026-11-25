(() => {
  "use strict";
  const explorer = document.querySelector("[data-visibility-explorer]");
  const archive = document.querySelector("[data-observation-archive]");
  if (!explorer || !archive) return;

  const observations = Array.from(archive.querySelectorAll("[data-observation-date]")).map((pass) => ({
    date: pass.dataset.observationDate,
    label: pass.querySelector("time").textContent,
    tiles: Array.from(pass.querySelectorAll("[data-grid]")).map((row) => ({
      grid: row.dataset.grid, visible: Number(row.dataset.visible),
      sampled: Number(row.dataset.sampled), vegetation: Number(row.dataset.vegetation),
    })),
  }));
  if (!observations.length || observations.some((pass) => !pass.tiles.length)) return;
  const usable = observations.every((pass) => pass.tiles.every((tile) =>
    Number.isInteger(tile.visible) && Number.isInteger(tile.sampled) &&
    Number.isInteger(tile.vegetation) && tile.sampled > 0 &&
    tile.visible >= 0 && tile.visible <= tile.sampled &&
    tile.vegetation >= 0 && tile.vegetation <= tile.visible
  ));
  if (!usable) return;

  const gridButtons = Array.from(explorer.querySelectorAll("[data-select-grid]"));
  const dateButtons = Array.from(explorer.querySelectorAll("[data-select-date]"));
  const bestButton = explorer.querySelector("[data-select-best]");
  let selectedGrid = gridButtons[0].dataset.selectGrid;
  let selectedDate = observations[0].date;
  const number = new Intl.NumberFormat("en-KE");
  const label = (visible, sampled) => {
    const percent = visible / sampled * 100;
    if (visible === 0) return "0%";
    return percent < 0.1 ? "<0.1%" : percent.toFixed(1) + "%";
  };
  const text = (selector, value) => { explorer.querySelector(selector).textContent = value; };
  const gridIn = (pass) => pass.tiles.find((tile) => tile.grid === selectedGrid);
  const bestPass = () => observations.reduce((best, pass) => {
    const candidate = gridIn(pass), previous = gridIn(best);
    return candidate.visible / candidate.sampled > previous.visible / previous.sampled ? pass : best;
  }, observations[0]);

  function readLocation() {
    const params = new URL(window.location.href).searchParams;
    const grid = params.get("grid"), date = params.get("date");
    selectedGrid = gridButtons.some((button) => button.dataset.selectGrid === grid) ? grid : gridButtons[0].dataset.selectGrid;
    selectedDate = observations.some((pass) => pass.date === date) ? date : bestPass().date;
  }
  function writeLocation() {
    const url = new URL(window.location.href);
    url.searchParams.set("grid", selectedGrid);
    url.searchParams.set("date", selectedDate);
    window.history.replaceState(null, "", url.pathname + url.search + url.hash);
  }

  // Only exact manifest-matched image crops may accompany the selected aggregate.
  const contextImages = {
    "T36MZE:2026-11-08": {
      src: "/assets/geta-context-2026-11-08.png",
      alt: "Actual 8 November 2026 Sentinel-2 image: green land, dark shadows and bright clouds in the provisional research window.",
      heading: "Land between clouds. An incomplete view.",
      caption: "The image shows the research window. The coverage chart counts surface-classified 20 m centres across the same window in this grid. White areas in the image are not a forest-loss classification.",
    },
    "T36MZE:2026-11-13": {
      src: "/assets/geta-context-2026-11-13.png",
      alt: "Actual 13 November 2026 Sentinel-2 image: almost entirely white, with almost no usable ground view.",
      heading: "A newer pass with almost no usable ground view.",
      caption: "The white is present in the source image. Almost all sampled centres were unassessed on this pass. We need a usable observation before assessing change.",
    },
  };
  const sceneImage = explorer.querySelector("[data-scene-image]");
  let matchingScene = null;
  let sceneFailed = false;
  function sceneStatus() {
    const available = Boolean(matchingScene) && !sceneFailed;
    explorer.querySelector("[data-scene-available]").hidden = !available;
    explorer.querySelector("[data-scene-empty]").hidden = available;
    text("[data-scene-heading]", available ? matchingScene.heading : "The counts and the source image are separate.");
    text("[data-scene-caption]", available ? matchingScene.caption : "A missing image crop does not mean zero visibility. Use the verified counts and their observation date on the right.");
    text("[data-scene-missing]", sceneFailed
      ? "The matching source image could not load. Coverage counts are still available; reload to try the image again."
      : "No published image crop matches " + selectedGrid + " on " + selectedDate + ". The coverage counts remain available.");
  }
  sceneImage.addEventListener("error", () => { sceneFailed = true; sceneStatus(); });
  sceneImage.addEventListener("load", () => { sceneFailed = false; sceneStatus(); });
  function updateScene(pass) {
    matchingScene = contextImages[selectedGrid + ":" + selectedDate] || null;
    if (matchingScene) {
      sceneImage.alt = matchingScene.alt;
      if (sceneImage.getAttribute("src") !== matchingScene.src) {
        sceneFailed = false;
        sceneImage.src = matchingScene.src;
      }
      text("[data-scene-date]", pass.label + " · " + selectedGrid);
    } else {
      sceneFailed = false;
      sceneImage.removeAttribute("src");
      sceneImage.alt = "";
    }
    sceneStatus();
  }

  function update(announce) {
    const pass = observations.find((item) => item.date === selectedDate);
    const tile = gridIn(pass);
    if (!tile) return;
    const percent = tile.visible / tile.sampled * 100;
    const share = label(tile.visible, tile.sampled);
    explorer.querySelector("[data-return-atlas]").href = "/atlas/geta?grid=" + encodeURIComponent(selectedGrid) + "&date=" + encodeURIComponent(selectedDate);
    updateScene(pass);
    gridButtons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.selectGrid === selectedGrid)));
    dateButtons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.selectDate === selectedDate));
      const item = observations.find((value) => value.date === button.dataset.selectDate);
      const grid = gridIn(item);
      const passShare = label(grid.visible, grid.sampled);
      button.querySelector("[data-pass-share]").textContent = passShare + " visible";
      button.querySelector("[data-pass-fill]").style.width = (grid.visible / grid.sampled * 100).toFixed(6) + "%";
      button.setAttribute("aria-label", item.label + ", " + passShare + " visible in " + selectedGrid);
    });
    text("[data-selected-grid]", tile.grid);
    text("[data-visible-percent]", share);
    text("[data-visible-caption]", number.format(tile.visible) + " of " + number.format(tile.sampled) + " centres");
    text("[data-visible-count]", number.format(tile.visible));
    text("[data-unassessed-count]", number.format(tile.sampled - tile.visible));
    text("[data-sampled-count]", number.format(tile.sampled));
    text("[data-vegetation-count]", number.format(tile.vegetation));
    const date = explorer.querySelector("[data-selected-date]");
    date.dateTime = pass.date;
    date.textContent = pass.label;
    explorer.querySelector("[data-coverage-fill]").style.width = percent.toFixed(6) + "%";
    explorer.querySelector("[data-coverage-arc]").setAttribute("stroke-dasharray", percent.toFixed(6) + " " + (100 - percent).toFixed(6));
    text("[data-coverage-title]", pass.label + ", " + selectedGrid + ": " + share + " visible; " + number.format(tile.sampled - tile.visible) + " of " + number.format(tile.sampled) + " centres unassessed.");

    const best = bestPass(), clearest = gridIn(best);
    bestButton.disabled = clearest.visible === 0;
    text("[data-best-summary]", clearest.visible === 0
      ? "None of these sampled passes provided a usable surface view in this grid."
      : "Among these sampled passes, " + best.label + " had the most usable coverage: " + label(clearest.visible, clearest.sampled) + ".");

    let interpretation;
    if (tile.visible === 0) {
      interpretation = "This pass left the entire sampled grid unassessed. Compare another pass for a more usable view. This does not mean the ground was unchanged.";
    } else if (percent < 1) {
      interpretation = "Only " + number.format(tile.visible) + " centres were usable. Most ground conditions remain unknown from this pass. Try the clearest sampled pass to understand the difference.";
    } else if (percent === 100) {
      interpretation = "All sampled centres were classified as surface on this pass. Usable coverage provides a view to assess; it does not by itself establish vegetation change.";
    } else {
      interpretation = "This pass provided a usable view of part of the grid. The remaining " + number.format(tile.sampled - tile.visible) + " centres were unassessed. Compare observations before drawing a conclusion about change.";
    }
    text("[data-interpretation]", interpretation);
    if (announce) {
      writeLocation();
      text("[data-selection-announcement]", tile.grid + ", " + pass.label + ". " + share + " visible. " + number.format(tile.sampled - tile.visible) + " centres unassessed.");
    }
  }

  gridButtons.forEach((button) => button.addEventListener("click", () => { selectedGrid = button.dataset.selectGrid; update(true); }));
  dateButtons.forEach((button) => button.addEventListener("click", () => { selectedDate = button.dataset.selectDate; update(true); }));
  bestButton.addEventListener("click", () => { selectedDate = bestPass().date; update(true); });
  window.addEventListener("popstate", () => { readLocation(); update(false); });
  readLocation();
  update(false);
  explorer.hidden = false;
  archive.open = false;
})();

// The historical source comparison is independent of the rolling report selection.
(() => {
  "use strict";
  const canvas = document.querySelector("[data-time-canvas]");
  const viewport = document.querySelector("[data-time-viewport]");
  const controls = document.querySelector("[data-time-controls]");
  if (!canvas || !viewport || !controls) return;
  const failure = document.querySelector("[data-time-failure]");
  const images = Array.from(canvas.querySelectorAll("[data-time-image]"));
  const reveal = controls.querySelector("[data-time-reveal]");
  const zoom = controls.querySelector("[data-time-zoom]");
  const checkImages = () => {
    const failed = images.filter(image => image.dataset.failed === "true");
    failure.hidden = failed.length === 0;
    failure.textContent = failed.length ? "The " + failed.map(image => image.dataset.timeImage).join(" and ") + " source image could not load. Reload to try again; no other date is substituted." : "";
    controls.hidden = failed.length > 0;
    viewport.classList.toggle("time-interactive", failed.length === 0);
  };
  images.forEach(image => {
    image.addEventListener("load", () => { delete image.dataset.failed; checkImages(); });
    image.addEventListener("error", () => { image.dataset.failed = "true"; checkImages(); });
    if (image.complete && image.currentSrc && image.naturalWidth === 0) image.dataset.failed = "true";
  });
  reveal.addEventListener("input", () => canvas.style.setProperty("--reveal", reveal.value + "%"));
  zoom.addEventListener("input", () => { canvas.style.width = zoom.value + "%"; });
  document.querySelector("[data-time-help]").textContent = "Move the comparison slider to reveal each date. Magnify both together, then scroll or use arrow keys in the image viewport to explore the same location.";
  const archive = document.querySelector("[data-observation-archive]");
  document.querySelectorAll("[data-time-coverage]").forEach(node => {
    const date = node.dataset.timeCoverage;
    const pass = Array.from(archive?.querySelectorAll("[data-observation-date]") || []).find(item => item.dataset.observationDate === date);
    const row = Array.from(pass?.querySelectorAll("[data-grid]") || []).find(item => item.dataset.grid === "T36MZE");
    if (!row) { node.textContent = "Coverage is not available in the current report."; return; }
    const visible = Number(row.dataset.visible), sampled = Number(row.dataset.sampled);
    if (!Number.isInteger(visible) || !Number.isInteger(sampled) || sampled <= 0 || visible < 0 || visible > sampled) return;
    const percent = 100 * visible / sampled;
    const formatted = percent === 0 ? "0%" : percent < .1 ? "<0.1%" : percent.toFixed(1) + "%";
    const format = new Intl.NumberFormat("en-KE");
    node.textContent = formatted + " usable · " + format.format(visible) + " of " + format.format(sampled) + " sampled centres";
  });
  checkImages();
})();
