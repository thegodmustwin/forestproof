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
    selectedDate = observations.some((pass) => pass.date === date) ? date : observations[0].date;
  }
  function writeLocation() {
    const url = new URL(window.location.href);
    url.searchParams.set("grid", selectedGrid);
    url.searchParams.set("date", selectedDate);
    window.history.replaceState(null, "", url.pathname + url.search + url.hash);
  }

  function update(announce) {
    const pass = observations.find((item) => item.date === selectedDate);
    const tile = gridIn(pass);
    if (!tile) return;
    const percent = tile.visible / tile.sampled * 100;
    const share = label(tile.visible, tile.sampled);
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
