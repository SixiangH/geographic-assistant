"use strict";

// Reading-first guided study. Answers stay in this browser / 阅读优先，答案仅保存在浏览器。
(() => {
  let current = null, selected = null, view = "concepts", generation = 0, lastCardRequest = -1, writes = Promise.resolve();
  const drafts = new Map();
  const panel = $(".explore-panel"), summary = $(".material-summary-panel");
  const progress = element("div", "guided-completion guided-task-status");
  progress.id = "guided-task-status"; progress.setAttribute("role", "status"); progress.setAttribute("aria-live", "polite");
  panel.querySelector(".panel-heading").after(progress);
  const nav = element("div", "simple-study-nav"); nav.setAttribute("role", "tablist"); nav.setAttribute("aria-label", "Guided learning activities");
  const content = element("section", "simple-study-content"); content.id = "simple-study-content"; content.setAttribute("role", "tabpanel");
  summary.after(nav, content);
  const scrollRegion = element("div", "explore-scroll"); scrollRegion.id = "explore-scroll";
  panel.append(scrollRegion);
  for (const child of [...panel.children]) {
    if (child !== scrollRegion && child !== progress && !child.classList.contains("panel-heading")) scrollRegion.append(child);
  }
  function button(text, action, cls = "text-button") {
    const b = element("button", cls, text); b.type = "button";
    b.addEventListener("click", () => Promise.resolve().then(action).catch(e => toast(e.message))); return b;
  }
  for (const [key, label] of [["concepts", "Unfamiliar concepts"], ["quiz", "Quick quiz"], ["explore", "Explore"]]) {
    const b = button(label, () => switchView(key), "tab"); b.id = `guided-tab-${key}`; b.dataset.view = key;
    b.setAttribute("role", "tab"); b.setAttribute("aria-controls", key === "explore" ? "card-view" : content.id); nav.append(b);
  }
  nav.addEventListener("keydown", event => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault(); const buttons = [...nav.children], i = buttons.indexOf(document.activeElement);
    const index = event.key === "Home" ? 0 : event.key === "End" ? 2 : (i + (event.key === "ArrowRight" ? 1 : -1) + 3) % 3;
    buttons[index].click(); buttons[index].focus();
  });
  function candidates() {
    const items = new Map();
    for (const m of state.mentions) {
      if (!m.id || m.kind !== "explicit") continue;
      const item = items.get(m.id) || {...m, frequency: 0}; item.frequency++; items.set(m.id, item);
    }
    return [...items.values()].sort((a, b) => b.frequency - a.frequency || a.start - b.start);
  }
  function status() {
    $("#study-mode").value = current?.mode || "guided";
    $("#study-start").disabled = !state.analysis;
    $("#study-start").textContent = "Choose unfamiliar concepts";
    $("#study-check").hidden = true;
    const due = $("#study-due"); if (due) due.textContent = "";
    $("#study-results").textContent = "Learning progress";
    $("#study-progress").textContent = !state.analysis ? "Start with a reading. Choose only concepts you do not know, then read and compare at your own pace."
      : current?.mode === "guided" ? "Read first. Compare your understanding whenever you are ready, then try the short quiz." : "Read and explore at your own pace.";
    const guided = Boolean(current?.mode === "guided"); nav.hidden = !guided; content.hidden = !guided || view === "explore";
    for (const child of scrollRegion.children) {
      if ([nav, content, summary].includes(child)) continue;
      child.hidden = guided && view !== "explore";
    }
    if (guided) {
      for (const b of nav.children) { b.setAttribute("aria-selected", String(b.dataset.view === view)); b.tabIndex = b.dataset.view === view ? 0 : -1; }
      content.setAttribute("aria-labelledby", `guided-tab-${view}`);
    }
    refreshProgress();
  }
  function switchView(next) { view = next; status(); if (view !== "explore") render(); scrollRegion.scrollTop = 0; }
  function completion() {
    const targets = current?.targets || [];
    const compared = targets.filter(t => t.understanding?.trim() && t.reference).length;
    const questions = current?.quiz?.questions || [];
    const answered = questions.filter(q => current.answers[q.id]).length;
    const box = element("div", "guided-completion"); box.setAttribute("aria-live", "polite");
    box.append(element("p", "small", !targets.length ? "Unfamiliar concepts: none selected" : `${compared === targets.length ? "✓ Completed" : "In progress"} · Unfamiliar concepts ${compared}/${targets.length}`),
      element("p", "small", !questions.length ? "Quiz: not available yet" : `${answered === questions.length ? "✓ Completed" : "In progress"} · Questions ${answered}/${questions.length}`));
    return box;
  }
  function refreshProgress() { progress.replaceChildren(...completion().childNodes); }
  function save(record = current) {
    if (!record) return Promise.resolve(true);
    record.updatedAt = Date.now(); const snapshot = structuredClone(record);
    writes = writes.then(async () => {
      try { await personalStore.put("study", snapshot); $("#study-storage-warning").hidden = true; return true; }
      catch (error) { $("#study-storage-warning").textContent = "Your learning progress was not saved. " + error.message; $("#study-storage-warning").hidden = false; return false; }
    }); return writes;
  }
  async function flush() {
    for (const [id, draft] of drafts) {
      const target = current?.targets.find(t => t.id === id); if (target) target.draft = draft;
    }
    drafts.clear(); if (current) await save(); await writes;
  }
  async function onMaterial(restored, mode = "guided") {
    await flush(); const ticket = ++generation;
    const id = state.historyId || "sample";
    let record = await personalStore.get("study", id);
    if (ticket !== generation) return;
    if (record && record.workflow !== "reading-first") {
      await personalStore.put("study", {...record, id: crypto.randomUUID(), archived: true}); record = null;
    }
    current = record || {id, materialId: state.historyId, title: state.title, createdAt: Date.now(), workflow: "reading-first", version: 2,
      mode: restored ? "guided" : mode, targets: [], quiz: structuredClone(state.analysis.study_quiz || {kind: "unavailable", questions: [], warning: "Generate a short quiz for this reading when you are ready."}), answers: {}};
    selected = current.targets[0]?.id || null; view = "concepts";
    summary.open = true; scrollRegion.scrollTop = 0;
    await save(); status(); render();
    if (!restored && mode === "guided") setup();
  }
  function setup() {
    if (!state.analysis) { openMaterial(); return; }
    const list = $("#study-targets"); list.replaceChildren();
    for (const item of candidates()) {
      const label = element("label"), input = element("input"); input.type = "checkbox"; input.value = item.id;
      input.checked = Boolean(current?.targets.some(t => t.id === item.id));
      label.append(input, element("span", "", `${item.title} · ${item.frequency} ${item.frequency === 1 ? "mention" : "mentions"}`)); list.append(label);
    }
    $("#study-setup-error").hidden = true; $("#study-setup").showModal();
  }
  $("#study-setup-form").addEventListener("submit", async event => {
    event.preventDefault(); const submit = event.submitter; submit.disabled = true;
    const old = current.targets, mode = current.mode, oldArchive = current.conceptArchive;
    current.conceptArchive = {...(current.conceptArchive || {}), ...Object.fromEntries(old.map(t => [t.id, t]))};
    const chosen = new Set($$("#study-targets input:checked").map(i => i.value));
    current.targets = candidates().filter(m => chosen.has(m.id)).map(m => old.find(t => t.id === m.id) || current.conceptArchive[m.id] || {id: m.id, title: m.title, understanding: "", draft: "", reference: null, comparedAt: null});
    current.mode = "guided";
    if (await save()) { selected = current.targets[0]?.id || null; $("#study-setup").close(); switchView("concepts"); toast("Your reading is ready. Compare the concepts whenever you want."); }
    else { current.targets = old; current.mode = mode; current.conceptArchive = oldArchive; }
    submit.disabled = false;
  });
  $("#study-cancel-setup").addEventListener("click", () => {
    $("#study-setup").close(); switchView("concepts");
  });
  function render() {
    content.replaceChildren(); if (!current || current.mode !== "guided") return;
    refreshProgress();
    if (view === "quiz") { renderQuiz(); return; }
    content.append(element("p", "small muted", "Read the material on the left. Choose a concept below whenever you are ready to explain it in your own words."));
    content.append(button("Choose or change unfamiliar concepts", setup));
    if (!current.targets.length) { content.append(element("p", "", "No unfamiliar concepts selected. You can keep reading, choose some later, or try the quick quiz.")); return; }
    const list = element("div", "guided-concept-list");
    for (const target of current.targets) {
      const b = button(`${target.understanding?.trim() && target.reference ? "✓ " : ""}${target.title}`, async () => { await flush(); selected = target.id; render(); }, "button");
      b.setAttribute("aria-pressed", String(target.id === selected)); list.append(b);
    }
    content.append(list);
    const t = current.targets.find(t => t.id === selected) || current.targets[0]; selected = t.id;
    content.append(element("h3", "", t.title));
    const form = element("form"), label = element("label", "", "My understanding"); label.htmlFor = "concept-understanding";
    const answer = element("textarea"); answer.id = "concept-understanding"; answer.rows = 3; answer.maxLength = 3000; answer.required = true;
    answer.placeholder = "One or two sentences is enough. You can describe what you think or what you are unsure about.";
    answer.value = drafts.get(t.id) ?? t.draft ?? t.understanding;
    answer.addEventListener("input", () => { t.draft = answer.value; drafts.set(t.id, answer.value); save(); });
    const error = element("p", "error"); error.hidden = true; error.setAttribute("role", "alert");
    const submit = element("button", "button primary", "Submit and compare"); submit.type = "submit";
    form.append(label, answer, error, submit); content.append(form);
    form.addEventListener("submit", async event => {
      event.preventDefault(); submit.disabled = true; error.hidden = true;
      const ticket = generation, record = current;
      try {
        const reference = t.reference || state.cards.get(t.id)?.card || (await api(`/api/card?id=${encodeURIComponent(t.id)}`)).card;
        if (ticket !== generation || record !== current) return;
        const previous = {...t}; t.understanding = answer.value.trim(); t.draft = t.understanding; t.reference = structuredClone(reference); t.comparedAt = Date.now();
        if (!await save()) { Object.assign(t, previous); throw new Error("Your understanding was not saved. Please try again."); }
        drafts.delete(t.id); render();
      } catch (failure) { error.textContent = failure.message; error.hidden = false; }
      finally { submit.disabled = false; }
    });
    if (t.understanding && t.reference) {
      const box = element("section", "guided-comparison");
      box.append(element("h4", "", "Compare with the source explanation"), element("p", "", t.reference.definition), element("p", "small muted", "An attributed knowledge-library or encyclopedia explanation; read the source to check details."));
      for (const source of t.reference.sources || []) box.append(safeLink(source.title, source.url));
      content.append(box);
    }
  }
  function renderQuiz() {
    const questions = current.quiz?.questions || [];
    content.append(element("p", "small muted", "Up to five AI-generated multiple-choice and true/false questions based on this material. Pick an answer to see feedback. You can still refer to the reading."));
    if (!questions.length) {
      content.append(element("p", "", current.quiz?.warning || "No quiz generated yet."));
      if (state.status.ai_available) content.append(button("Generate short quiz", async () => {
        const ticket = generation, record = current; const b = $("#generate-short-quiz"); b.disabled = true; b.textContent = "Preparing questions…";
        try {
          const result = await api("/api/study-quiz", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({text: state.text, session_id: state.session})});
          updateUsage(result.usage, {});
          if (ticket !== generation || record !== current) return;
          const old = current.quiz; current.quiz = result.quiz;
          if (!await save()) { current.quiz = old; throw new Error("Quiz was not saved. Please retry."); }
          state.analysis.study_quiz = result.quiz; await persistHistoryAnalysis(); render();
        } finally { if (b.isConnected) { b.disabled = false; b.textContent = "Generate short quiz"; } }
      }, "button primary"));
      const generate = content.querySelector("button.primary"); if (generate) generate.id = "generate-short-quiz";
      return;
    }
    if (current.quiz.warning) content.append(element("p", "small muted", current.quiz.warning));
    questions.forEach((q, i) => {
      const box = element("section", "guided-quiz-question"); box.dataset.question = q.id;
      box.append(element("p", "eyebrow", `${i + 1} / ${questions.length} · ${q.type === "true_false" ? "TRUE OR FALSE" : "MULTIPLE CHOICE"}`), element("h3", "", q.question));
      const answered = current.answers[q.id];
      q.options.forEach((option, index) => {
        const b = button(option, async () => {
          const previous = current.answers[q.id]; current.answers[q.id] = {choice: index, correct: index === q.answer, answeredAt: Date.now()};
          if (!await save()) { if (previous) current.answers[q.id] = previous; else delete current.answers[q.id]; toast("Your answer was not saved. Try again."); }
          render();
        }, "button quiz-option"); b.disabled = Boolean(answered); b.setAttribute("aria-pressed", String(answered?.choice === index)); box.append(b);
      });
      if (answered) {
        const feedback = element("div", answered.correct ? "quiz-feedback correct" : "quiz-feedback incorrect"); feedback.setAttribute("role", "status");
        feedback.append(element("strong", "", answered.correct ? "Correct" : `Not quite. Correct answer: ${q.options[q.answer]}`), element("p", "", q.explanation), element("blockquote", "", q.evidence), element("p", "small muted", "Evidence from your material. AI-generated feedback can still need teacher review.")); box.append(feedback);
      }
      content.append(box);
    });
  }
  function renderGate() { return false; }
  function afterCard() {
    if (!state.card || state.requestSequence === lastCardRequest) return;
    lastCardRequest = state.requestSequence;
    const showExplanation = () => { scrollRegion.scrollTop = Math.max(0, $("#card-view").offsetTop - 12); };
    if (current?.mode !== "guided") { showExplanation(); return; }
    if (state.returnTo === "saved" || state.returnTo === "library") { switchView("explore"); showExplanation(); return; }
    // A highlighted term opens normal Explore. Selected unfamiliar terms open the reflection panel.
    if (state.card && state.selectedMention !== null) {
      if (current.targets.some(t => t.id === state.card.id)) { selected = state.card.id; switchView("concepts"); }
      else { switchView("explore"); showExplanation(); }
    }
  }
  function historyAction(actions, entry) {
    actions.append(button("Study / review", async () => { await restoreHistory(entry.id); switchView("concepts"); }));
  }
  async function removeForHistory(id) {
    await flush();
    for (const r of await personalStore.list("study")) if (!id || r.materialId === id) await personalStore.delete("study", r.id);
    if (current && (!id || current.materialId === id)) { current = null; selected = null; generation++; status(); }
  }
  $("#study-start").addEventListener("click", setup);
    $("#study-results").addEventListener("click", () => { if (!state.analysis) openMaterial(); else switchView("concepts"); });
  $("#study-mode").addEventListener("change", async event => {
    if (!state.analysis) { $("#study-mode").value = "guided"; openMaterial(); return; }
    const old = current.mode; current.mode = event.target.value;
    if (!await save()) current.mode = old;
    status(); renderCard(); if (current.mode === "guided") { switchView("concepts"); if (!current.targets.length) setup(); }
  });
  window.atlasStudy = {onMaterial, renderGate, afterCard, historyAction, removeForHistory, isGuided: () => current?.mode === "guided"};
  status();
})();
