(() => {
  "use strict";

  const explorer = document.querySelector("[data-visibility-explorer]");
  const archive = document.querySelector("[data-observation-archive]");
  if (!explorer || !archive) return;

  const observations = Array.from(archive.querySelectorAll("[data-observation-date]")).map((pass) => ({
    date: pass.dataset.observationDate,
    label: pass.querySelector("time").textContent,
    tiles: Array.from(pass.querySelectorAll("[data-grid]")).map((row) => ({
      grid: row.dataset.grid,
      visible: Number(row.dataset.visible),
      sampled: Number(row.dataset.sampled),
      vegetation: Number(row.dataset.vegetation),
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
  let selectedGrid = gridButtons[0].dataset.selectGrid;
  let selectedDate = observations[0].date;
  const number = new Intl.NumberFormat("en-KE");
  const label = (visible, sampled) => {
    const percent = visible / sampled * 100;
    if (visible === 0) return "0%";
    return percent < 0.1 ? "<0.1%" : percent.toFixed(1) + "%";
  };
  const text = (selector, value) => {
    explorer.querySelector(selector).textContent = value;
  };

  function update(announce) {
    const pass = observations.find((item) => item.date === selectedDate);
    const tile = pass.tiles.find((item) => item.grid === selectedGrid);
    if (!tile) return;
    const percent = tile.visible / tile.sampled * 100;
    const share = label(tile.visible, tile.sampled);
    gridButtons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.selectGrid === selectedGrid));
    });
    dateButtons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.selectDate === selectedDate));
      const item = observations.find((value) => value.date === button.dataset.selectDate);
      const grid = item.tiles.find((value) => value.grid === selectedGrid);
      button.querySelector("[data-pass-share]").textContent = label(grid.visible, grid.sampled) + " visible";
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

    let interpretation;
    if (tile.visible === 0) {
      interpretation = "This pass left the entire sampled grid unassessed. Compare an earlier pass or check again for a clearer view.";
    } else if (percent < 1) {
      interpretation = "Only " + number.format(tile.visible) + " centres were usable. Most ground conditions remain unknown from this pass.";
    } else {
      interpretation = "This pass provides a partial surface view. Use it alongside another observation when reviewing a possible change.";
    }
    text("[data-interpretation]", interpretation);
    if (announce) {
      text("[data-selection-announcement]", tile.grid + ", " + pass.label + ". " +
        share + " visible. " + number.format(tile.sampled - tile.visible) + " centres unassessed.");
    }
  }

  gridButtons.forEach((button) => {
    button.addEventListener("click", () => {
      selectedGrid = button.dataset.selectGrid;
      update(true);
    });
  });
  dateButtons.forEach((button) => {
    button.addEventListener("click", () => {
      selectedDate = button.dataset.selectDate;
      update(true);
    });
  });

  update(false);
  explorer.hidden = false;
  archive.open = false;
})();
