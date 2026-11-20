/* ForestProof public tour. Fictional browser-only state; no requests or storage. */
(() => {
  "use strict";

  const root = document.documentElement;
  const panels = Array.from(document.querySelectorAll("[data-tour-panel]"));
  const links = Array.from(document.querySelectorAll("[data-tour-step]"));
  if (panels.length !== 5 || links.length !== 5) return;

  const names = ["signal", "review", "response", "follow-up", "dossier"];
  const state = { step: 0, opened: false, review: null, response: false, followup: null, recordedAt: { opened: null, review: null, response: null, followup: null } };
  let selectedRecord = "observation";
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


  const recordKinds = ["receipt", "observation", "case", "review", "response", "followup", "dossier"];
  const recordLabels = { receipt: "Source receipt", observation: "Observation", case: "Case", review: "Review decision", response: "Response", followup: "Follow-up", dossier: "Dossier" };
  const recordIds = { receipt: "SIM-RECEIPT-01", observation: "SIM-OBS-01", case: "SIM-CASE-01", review: "SIM-REVIEW-01", response: "SIM-RESPONSE-01", followup: "SIM-FOLLOWUP-01", dossier: "SIM-DOSSIER-01" };
  const relationships = [["receipt", "observation", "describes"], ["observation", "case", "reviewed in"], ["case", "review", "has review"], ["review", "response", "guides"], ["response", "followup", "checked by"], ["followup", "dossier", "included in"]];
  const sourceLimits = "Cause, field conditions, authorization and environmental impact remain unknown.";
  const nextStage = { receipt: 0, observation: 0, case: 0, review: 1, response: 2, followup: 3, dossier: 3 };
  const browserTime = value => value ? value + " (browser action, UTC)" : "Not recorded";

  function recordModel() {
    const available = { receipt: true, observation: true, case: state.opened, review: Boolean(state.review), response: state.response, followup: Boolean(state.followup), dossier: complete() };
    const details = {
      receipt: { description: "The in-page synthetic receipt describes SIM-OBS-01. It keeps the source identity connected to the case; no original file or evidence hash is represented.", actor: "Fictional source fixture", time: "Example Day 1, 09:15 (fictional observation time)", fields: [["Receipt type", "Synthetic in-page description"], ["Source", recordIds.observation]] },
      observation: { description: "The fictional signal suggests possible vegetation change. The same source identity stays attached to every later record.", actor: "Fictional source fixture", time: "Example Day 1, 09:15 (fictional observation time)", fields: [["Representation", "Illustrative signal; no measured index or real location"], ["Receipt", recordIds.receipt]] },
      case: { description: "Opening the example case gives the review a responsible role and preserves its original observation link.", actor: "Example reviewer (fictional)", time: browserTime(state.recordedAt.opened), fields: [["Question", "Review the sample vegetation signal"], ["Observation", recordIds.observation]] },
      review: { description: state.review ? reviewText[state.review] : "Choose and record a review question before this record becomes available.", actor: "Example reviewer (fictional)", time: browserTime(state.recordedAt.review), fields: [["Choice", state.review || "Not recorded"], ["Case", recordIds.case]] },
      response: { description: state.response ? responseText[state.review] : "Record the review and its proposed response to create this record.", actor: "Example reviewer (fictional)", time: browserTime(state.recordedAt.response), fields: [["Next check", "Example Day 8"], ["Review", state.review ? recordIds.review : "Not recorded"]] },
      followup: { description: state.followup ? followupText[state.followup] : "Record the response and choose a fictional follow-up result to create this record.", actor: "Example reviewer (fictional)", time: browserTime(state.recordedAt.followup), fields: [["Result", state.followup || "Not recorded"], ["Response", state.response ? recordIds.response : "Not recorded"]] },
      dossier: { description: "A derived, unsigned teaching projection connects the completed source, review, response and follow-up. The download creation time is recorded separately when exported.", actor: "Browser-only projection", time: complete() ? "Available after follow-up: " + browserTime(state.recordedAt.followup) : "Not assembled", fields: [["Classification", "FICTIONAL_DEMO · unsigned"], ["Conclusion", "Open for verification; impact unestablished"]] },
    };
    return recordKinds.map(key => ({ key, id: recordIds[key], title: recordLabels[key], available: Boolean(available[key]), ...details[key] }));
  }

  function renderRecordInspector(records, announce = false) {
    const record = records.find(item => item.key === selectedRecord);
    if (!record) return;
    text("[data-record-title]", record.title);
    text("[data-record-status]", record.available ? (record.key === "receipt" || record.key === "observation" ? "Fictional source · available" : "Fictional record · available") : "Not recorded yet");
    document.querySelector("[data-record-status]")?.setAttribute("data-available", String(record.available));
    text("[data-record-description]", record.available ? record.description : "This step has not been recorded in this tab. " + record.description);
    const fields = record.available ? [["Record ID", record.id], ["Actor", record.actor], ["Time", record.time], ...record.fields, ["Uncertainty", sourceLimits]] : [["Status", "Unavailable in the current example"], ["Needed next", record.key === "case" ? "Open a demo case" : record.key === "dossier" ? "Complete review, response and follow-up" : "Complete the required earlier steps"], ["Source", recordIds.observation]];
    const list = document.querySelector("[data-record-fields]");
    if (list) list.replaceChildren(...fields.map(([label, value]) => { const row = document.createElement("div"), dt = document.createElement("dt"), dd = document.createElement("dd"); dt.textContent = label; dd.textContent = value; row.append(dt, dd); return row; }));
    const related = relationships.flatMap(([from, to]) => from === record.key ? [to] : to === record.key ? [from] : []).filter(key => records.some(item => item.key === key && item.available));
    const links = document.querySelector("[data-record-links]");
    if (links) links.replaceChildren(...(record.available ? related : []).map(key => { const button = document.createElement("button"); button.type = "button"; button.textContent = recordLabels[key]; button.dataset.relatedRecord = key; button.addEventListener("click", () => { selectedRecord = key; updateRecordGraph(true); }); return button; }));
    const jump = document.querySelector("[data-record-jump]");
    if (jump) {
      jump.hidden = record.available;
      jump.dataset.stage = String(!state.opened ? 0 : !state.review ? 1 : !state.response ? 2 : nextStage[record.key]);
    }
    document.querySelectorAll("[data-record-node]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.recordNode === record.key)));
    if (announce) text("[data-record-announcement]", record.title + ". " + (record.available ? "Record available." : "Not recorded yet."));
  }

  function updateRecordGraph(announce = false) {
    const records = recordModel();
    text("[data-record-count]", records.filter(record => record.available).length + " of 7 records available");
    document.querySelectorAll("[data-record-node]").forEach(button => {
      const record = records.find(item => item.key === button.dataset.recordNode);
      if (!record) return;
      button.dataset.available = String(record.available);
      button.setAttribute("aria-label", record.title + ", " + (record.available ? record.id : "not recorded yet"));
      button.querySelector("small").textContent = record.available ? record.id : "Not recorded yet";
    });
    document.querySelectorAll("[data-record-edge]").forEach(edge => {
      const [from, to] = edge.dataset.recordEdge.split(":");
      edge.toggleAttribute("hidden", !records.some(record => record.key === from && record.available) || !records.some(record => record.key === to && record.available));
    });
    renderRecordInspector(records, announce);
  }

  document.querySelectorAll("[data-record-node]").forEach(button => button.addEventListener("click", () => { selectedRecord = button.dataset.recordNode; updateRecordGraph(true); }));
  document.querySelector("[data-record-jump]")?.addEventListener("click", event => { show(Number(event.currentTarget.dataset.stage), { focus: true }); });
  const evidenceBrowser = document.querySelector("[data-evidence-browser]");
  if (evidenceBrowser && window.matchMedia("(max-width: 760px)").matches) evidenceBrowser.open = false;

  function updateReceipt() {
    const completed = [state.opened, Boolean(state.review), state.response, Boolean(state.followup), Boolean(state.followup)];
    const recorded = completed.slice(0, 4).filter(Boolean).length;
    text("[data-tour-progress-count]", recorded + " of 4");
    const progress = document.querySelector("[data-tour-progress-fill]");
    if (progress) progress.style.width = recorded / 4 * 100 + "%";
    document.querySelectorAll("[data-tour-download], [data-tour-print]").forEach(button => {
      button.disabled = !complete();
    });
    links.forEach((link, index) => link.classList.toggle("is-complete", completed[index]));
    text("[data-tour-case-state]", state.followup ? "Open for verification" : state.response ? "Demo response recorded" : state.review ? "Under example review" : state.opened ? "Demo case opened" : "DEMO observation");
    text('[data-tour-summary="review"]', state.review ? reviewText[state.review] : "No interactive review recorded");
    text('[data-tour-summary="response"]', state.response ? responseText[state.review] : "No interactive response recorded");
    text('[data-tour-summary="followup"]', state.followup ? followupText[state.followup] : "No interactive follow-up recorded");
    text("[data-tour-response-title]", state.review ? responseText[state.review] : responseText.later);
    text("[data-tour-response-note]", state.review === "quality"
      ? "Example reviewer will recheck the source quality and record any cloud, shadow or processing limitations before interpreting the sample signal."
      : "Example reviewer will compare the same sample location when a later usable capture is available. A signal alone will not be treated as a confirmed incident.");

    updateRecordGraph();
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
    selectedRecord = ["observation", "case", "review", "response", complete() ? "dossier" : "followup"][state.step];
    panels.forEach((panel, number) => { panel.hidden = number !== state.step; });
    links.forEach((link, number) => {
      if (number === state.step) link.setAttribute("aria-current", "step");
      else link.removeAttribute("aria-current");
    });
    updateReceipt();
    if (changeHash && location.hash !== "#" + names[state.step]) history.pushState(null, "", "#" + names[state.step]);
    if (focus) panels[state.step].querySelector("h2")?.focus();
  }

  function validation(name, message) {
    text('[data-tour-validation="' + name + '"]', message);
  }

  function choice(name) {
    return document.querySelector('input[name="' + name + '"]:checked')?.value ?? null;
  }

  function complete() {
    return state.opened && Object.hasOwn(reviewText, state.review) && state.response && Object.hasOwn(followupText, state.followup);
  }

  function dossier() {
    if (!complete()) return null;
    return {
      schema_version: "forestproof.fictional_walkthrough.v1",
      classification: "FICTIONAL_DEMO",
      unsigned: true,
      generated_at: new Date().toISOString(),
      case_id: "SIM-CASE-01",
      source: { record_id: "SIM-OBS-01", synthetic: true, observation_time: "Example Day 1, 09:15", representation: "Illustrative possible vegetation signal; no measured values or real location" },
      reviewer_role: "Example reviewer (fictional)",
      evidence_lineage: { records: recordModel().filter(record => record.available), relationships: relationships.map(([from, to, relation]) => ({ from: recordIds[from], to: recordIds[to], relation })), timestamp_meaning: "Browser-action UTC timestamps are distinct from fictional example observation/check times." },
      review: { choice: state.review, description: reviewText[state.review] },
      response: { description: responseText[state.review], checkpoint: "Example Day 8" },
      follow_up: { choice: state.followup, description: followupText[state.followup] },
      case_state: "Open for verification (fictional)",
      conclusion: "Cause, field conditions, authorization and environmental impact remain unestablished.",
      limits: ["Fictional browser-only teaching example. Not a real source receipt or field record.", "No identity verification or digital signature. No legal or environmental finding.", "The generated timestamp is the download creation time, not an observation time."]
    };
  }

  document.querySelector("[data-tour-download]")?.addEventListener("click", () => {
    const record = dossier();
    if (!record) {
      text("[data-tour-export-status]", "Complete the example review, response and follow-up before exporting.");
      return;
    }
    const file = new Blob([JSON.stringify(record, null, 2) + "\n"], { type: "application/json" });
    const url = URL.createObjectURL(file);
    const link = document.createElement("a");
    link.href = url;
    link.download = "ForestProof-FICTIONAL-DEMO-SIM-CASE-01.json";
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    text("[data-tour-export-status]", "Fictional, unsigned dossier prepared for download to your device. No data was sent.");
  });

  document.querySelector("[data-tour-print]")?.addEventListener("click", () => {
    if (!complete()) {
      text("[data-tour-export-status]", "Complete the example review, response and follow-up before printing.");
      return;
    }
    text("[data-tour-export-status]", "Print preview contains the fictional dossier. Choose Save as PDF in your browser to keep a copy.");
    window.print();
  });

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
    state.recordedAt.opened ??= new Date().toISOString();
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
    state.recordedAt.opened ??= new Date().toISOString();
    if (changed || !state.recordedAt.review) state.recordedAt.review = new Date().toISOString();
    state.review = selected;
    if (changed) {
      state.response = false;
      state.followup = null;
      state.recordedAt.response = null;
      state.recordedAt.followup = null;
      text("[data-tour-export-status]", "");
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
    state.recordedAt.response ??= new Date().toISOString();
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
    if (state.followup !== selected || !state.recordedAt.followup) state.recordedAt.followup = new Date().toISOString();
    state.followup = selected;
    validation("followup", "");
    show(4, { focus: true });
    notify("Demo follow-up recorded. The example remains open for verification; no environmental impact is claimed.");
  });

  document.querySelector("[data-tour-reset]")?.addEventListener("click", () => {
    Object.assign(state, { step: 0, opened: false, review: null, response: false, followup: null, recordedAt: { opened: null, review: null, response: null, followup: null } });
    document.querySelectorAll('input[type="radio"]').forEach(input => { input.checked = false; });
    document.querySelectorAll("[data-tour-validation]").forEach(element => { element.textContent = ""; });
    text("[data-tour-export-status]", "");
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
