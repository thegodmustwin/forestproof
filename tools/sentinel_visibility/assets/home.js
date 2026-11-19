"use strict";
(() => {
  const panel = document.querySelector("[data-image-comparison]");
  const input = document.querySelector("[data-image-reveal]");
  const earlier = document.querySelector(".scene-earlier");
  const line = document.querySelector("[data-split-line]");
  if (!panel || !input || !earlier || !line) return;
  panel.classList.add("enhanced");
  panel.querySelectorAll("img").forEach(image => { image.draggable = false; });
  document.querySelector("[data-compare-control]").hidden = false;
  function update() {
    const value = Math.min(100, Math.max(0, Number(input.value)));
    earlier.style.clipPath = "inset(0 " + (100 - value) + "% 0 0)";
    line.style.left = value + "%";
    input.setAttribute("aria-valuetext", value + "% of 8 November shown; " + (100 - value) + "% of 13 November shown");
  }
  input.addEventListener("input", update);
  let dragging = false;
  function revealAt(event) {
    const bounds = panel.getBoundingClientRect();
    input.value = String(Math.round(Math.min(100, Math.max(0, (event.clientX - bounds.left) / bounds.width * 100))));
    update();
  }
  panel.addEventListener("pointerdown", event => {
    if (!event.isPrimary || event.button !== 0) return;
    if (event.pointerType === "mouse") event.preventDefault();
    dragging = true;
    panel.setPointerCapture(event.pointerId);
    revealAt(event);
  });
  panel.addEventListener("pointermove", event => { if (dragging) revealAt(event); });
  panel.addEventListener("pointerup", () => { dragging = false; });
  panel.addEventListener("pointercancel", () => { dragging = false; });
  update();
})();
