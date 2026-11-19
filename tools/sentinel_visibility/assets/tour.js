/* ForestProof public tour. Fictional browser-only state; no requests or storage. */
(() => {
  "use strict";

  const root = document.documentElement;
  const panels = Array.from(document.querySelectorAll("[data-tour-panel]"));
  const links = Array.from(document.querySelectorAll("[data-tour-step]"));
  if (panels.length !== 5 || links.length !== 5) return;

  const names = ["signal", "review", "response", "follow-up", "dossier"];
  const state = { step: 0, opened: false, review: null, response: false, followup: null };
  const reviewText = {
    later: "Look for a later usable observation",
    quality: "Recheck the source quality first",
  };
  const responseText = {
    later: "Request another usable observation",
    quality: "Request a source-quality recheck",
  };
  const followupText = {
    persists: "Example signal persists; cause remains unknown",
    limited: "Example remains unresolved; usable evidence is insufficient",
  };
  const announcement = document.querySelector("[data-tour-announcement]");

  function text(selector, value) {
    const element = document.querySelector(selector);
    if (element) element.textContent = value;
  }

  function notify(message) {
    if (announcement) announcement.textContent = message;
  }

  function updateReceipt() {
    const completed = [state.opened, Boolean(state.review), state.response, Boolean(state.followup), Boolean(state.followup)];
    links.forEach((link, index) => link.classList.toggle("is-complete", completed[index]));
    text("[data-tour-case-state]", state.followup ? "Open for verification" : state.response ? "Demo response recorded" : state.review ? "Under example review" : state.opened ? "Demo case opened" : "DEMO observation");
    text('[data-tour-summary="review"]', state.review ? reviewText[state.review] : "No interactive review recorded");
    text('[data-tour-summary="response"]', state.response ? responseText[state.review] : "No interactive response recorded");
    text('[data-tour-summary="followup"]', state.followup ? followupText[state.followup] : "No interactive follow-up recorded");
    text("[data-tour-response-title]", state.review ? responseText[state.review] : responseText.later);
    text("[data-tour-response-note]", state.review === "quality"
      ? "Example reviewer will recheck the source quality and record any cloud, shadow or processing limitations before interpreting the sample signal."
      : "Example reviewer will compare the same sample location when a later usable capture is available. A signal alone will not be treated as a confirmed incident.");

    const ledger = document.querySelector("[data-tour-ledger]");
    if (!ledger) return;
    const entries = [["Sample signal received", "Day 1 · synthetic fixture"]];
    if (state.opened) entries.push(["Demo case opened", "Example reviewer · source retained"]);
    if (state.review) entries.push([reviewText[state.review], "Example review · uncertainty retained"]);
    if (state.response) entries.push([responseText[state.review], "Example response · next check on Day 8"]);
    if (state.followup) entries.push([followupText[state.followup], "Example follow-up · case stays open"]);
    ledger.replaceChildren(...entries.map(([label, detail]) => {
      const row = document.createElement("li");
      row.append(document.createTextNode(label));
      const note = document.createElement("span");
      note.textContent = detail;
      row.append(note);
      return row;
    }));
  }

  function show(index, { focus = false, changeHash = true } = {}) {
    state.step = Math.max(0, Math.min(4, index));
    panels.forEach((panel, number) => { panel.hidden = number !== state.step; });
    links.forEach((link, number) => {
      if (number === state.step) link.setAttribute("aria-current", "step");
      else link.removeAttribute("aria-current");
    });
    updateReceipt();
    if (changeHash && location.hash !== "#" + names[state.step]) history.pushState(null, "", "#" + names[state.step]);
    if (focus) panels[state.step].querySelector("h2")?.focus({ preventScroll: true });
  }

  function validation(name, message) {
    text('[data-tour-validation="' + name + '"]', message);
  }

  function choice(name) {
    return document.querySelector('input[name="' + name + '"]:checked')?.value ?? null;
  }

  links.forEach((link, index) => link.addEventListener("click", event => {
    event.preventDefault();
    show(index, { focus: true });
    notify("Showing the " + names[index] + " stage. Interactive choices stay in this browser tab.");
  }));

  document.querySelectorAll("[data-tour-back]").forEach(button => button.addEventListener("click", () => {
    show(state.step - 1, { focus: true });
    notify("Previous stage. Your example choices are unchanged.");
  }));

  document.querySelector('[data-tour-action="open"]')?.addEventListener("click", () => {
    state.opened = true;
    show(1, { focus: true });
    notify("Demo case opened in this page. Choose the review question you would pursue.");
  });

  document.querySelector('[data-tour-action="review"]')?.addEventListener("click", () => {
    const selected = choice("demo-review");
    if (!selected || !(selected in reviewText)) {
      validation("review", "Choose a review question before recording the example.");
      document.querySelector('input[name="demo-review"]')?.focus();
      return;
    }
    const changed = state.review !== selected;
    state.opened = true;
    state.review = selected;
    if (changed) {
      state.response = false;
      state.followup = null;
      document.querySelectorAll('input[name="demo-followup"]').forEach(input => { input.checked = false; });
    }
    validation("review", "");
    show(2, { focus: true });
    notify(changed ? "Example review recorded. The proposed response now follows your choice." : "Example review retained. Continue with the response.");
  });

  document.querySelector('[data-tour-action="response"]')?.addEventListener("click", () => {
    if (!state.review) {
      validation("response", "Record a review choice first. Use the Review stage above.");
      return;
    }
    state.response = true;
    validation("response", "");
    show(3, { focus: true });
    notify("Demo response recorded in the example receipt. No request was sent.");
  });

  document.querySelector('[data-tour-action="followup"]')?.addEventListener("click", () => {
    if (!state.response) {
      validation("followup", "Record the example response before adding a follow-up.");
      return;
    }
    const selected = choice("demo-followup");
    if (!selected || !(selected in followupText)) {
      validation("followup", "Choose a fictional follow-up result to complete the example.");
      document.querySelector('input[name="demo-followup"]')?.focus();
      return;
    }
    state.followup = selected;
    validation("followup", "");
    show(4, { focus: true });
    notify("Demo follow-up recorded. The example remains open for verification; no environmental impact is claimed.");
  });

  document.querySelector("[data-tour-reset]")?.addEventListener("click", () => {
    Object.assign(state, { step: 0, opened: false, review: null, response: false, followup: null });
    document.querySelectorAll('input[type="radio"]').forEach(input => { input.checked = false; });
    document.querySelectorAll("[data-tour-validation]").forEach(element => { element.textContent = ""; });
    show(0, { focus: true });
    notify("Tour reset. Nothing was saved or sent.");
  });

  function fromHash() {
    const requested = names.indexOf(location.hash.slice(1));
    show(requested < 0 ? 0 : requested, { changeHash: false });
  }
  window.addEventListener("popstate", fromHash);
  window.addEventListener("hashchange", fromHash);
  root.classList.add("tour-ready");
  fromHash();
})();
