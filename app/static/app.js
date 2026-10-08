"use strict";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const state = {
  text: "", title: "", mentions: [], filter: "all", highlights: true, tab: "learn", card: null,
  selectedMention: null, cards: new Map(), status: {}, world: null, quiz: new Map(),
  requestSequence: 0, searchSequence: 0, searchController: null,
  historyId: null, analysis: null, collection: "history", collectionSequence: 0,
  savedIds: new Set(), noteId: null, pendingDelete: null,
  session: crypto.randomUUID(), usage: { model_calls: 0, input_tokens: 0, output_tokens: 0, tool_requests: 0, cache_hits: 0, cost: 0, unknownCost: false },
};

function element(tag, className = "", text = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

function safeLink(text, url, className = "") {
  const node = element("a", className, text);
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== "https:") return element("span", className, text);
    node.href = parsed.href;
  } catch { return element("span", className, text); }
  node.target = "_blank";
  node.rel = "noopener noreferrer";
  return node;
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const payload = await response.json();
  if (!response.ok) {
    let message = typeof payload.detail === "string" ? payload.detail : "Please check your input and try again.";
    if (response.status >= 500 && typeof payload.detail !== "string") message = "The service is unavailable. Please try again.";
    throw new Error(message);
  }
  return payload;
}

function toast(message) {
  const node = $("#toast");
  node.textContent = message;
  node.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { node.hidden = true; }, 4000);
}

function updateUsage(usage = {}, retrieval = {}) {
  for (const key of ["model_calls", "input_tokens", "output_tokens"]) state.usage[key] += usage[key] || 0;
  state.usage.tool_requests += retrieval.tool_requests || 0;
  state.usage.cache_hits += usage.cache_hit || retrieval.origin === "cache" ? 1 : 0;
  if (usage.estimated_cost_usd === null) state.usage.unknownCost = true;
  else state.usage.cost += usage.estimated_cost_usd || 0;
  const u = state.usage;
  $("#session-usage").textContent = `${u.model_calls} model calls · ${u.input_tokens.toLocaleString()} input tokens · ${u.output_tokens.toLocaleString()} output tokens. ${u.tool_requests} source requests · ${u.cache_hits} cache hits. Estimated model cost: ${u.unknownCost ? "unavailable (prices not configured or a call failed)" : "$" + u.cost.toFixed(5)}. Cached cards do not call a model.`;
}

function renderPassage() {
  const container = $("#passage");
  container.replaceChildren();
  let cursor = 0;
  const fragment = document.createDocumentFragment();
  for (const [index, mention] of state.mentions.entries()) {
    const isPlace = ["country", "place", "physical"].includes(mention.category);
    const visible = state.highlights && (state.filter === "all" || (state.filter === "places" ? isPlace : !isPlace));
    if (!visible) continue;
    fragment.append(document.createTextNode(state.text.slice(cursor, mention.start)));
    const button = element("button", `mention ${isPlace ? "place" : "idea"} ${mention.kind === "inferred" ? "inferred" : ""} ${mention.category === "ambiguous" ? "ambiguous" : ""}`, state.text.slice(mention.start, mention.end));
    button.type = "button";
    button.dataset.index = index;
    button.title = mention.kind === "inferred" ? `Possible connection: ${mention.title}` : `Explore ${mention.title}`;
    button.setAttribute("aria-pressed", state.selectedMention === index ? "true" : "false");
    if (state.selectedMention === index) button.classList.add("selected");
    button.addEventListener("click", () => selectMention(index));
    fragment.append(button);
    cursor = mention.end;
  }
  fragment.append(document.createTextNode(state.text.slice(cursor)));
  container.append(fragment);
}

function renderIndex() {
  const unique = new Map();
  state.mentions.forEach((m, i) => { if (!unique.has(m.id || m.text)) unique.set(m.id || m.text, { m, i }); });
  $("#concept-count").textContent = `${unique.size} concepts`;
  const list = $("#concept-list");
  list.replaceChildren();
  for (const { m, i } of unique.values()) {
    const button = element("button", "concept-pill", m.title);
    button.addEventListener("click", () => {
      selectMention(i);
      const highlighted = $(`.mention[data-index="${i}"]`);
      highlighted?.scrollIntoView({ block: "nearest" });
    });
    list.append(button);
  }
  if (!unique.size) list.append(element("p", "small muted", "No local concepts found. Search the library or enable AI assistance if configured."));
}

function activateMention(index) {
  state.selectedMention = index;
  $$(".mention").forEach(node => {
    const active = Number(node.dataset.index) === index;
    node.classList.toggle("selected", active);
    node.setAttribute("aria-pressed", String(active));
  });
}

function selectMention(index) {
  const mention = state.mentions[index];
  activateMention(index);
  state.tab = "learn";
  renderTabs();
  if (!mention.id) {
    state.requestSequence++;
    state.card = null;
    const view = $("#card-view");
    view.replaceChildren(element("p", "card-category", "Choose a meaning"), element("h3", "card-title", mention.text), element("p", "card-definition", "This name can refer to more than one place. Which meaning fits your passage?"));
    for (const candidate of mention.candidates) {
      const button = element("button", "choice-button", candidate.title);
      button.append(element("small", "", candidate.category));
      button.addEventListener("click", () => {
        mention.id = candidate.id;
        mention.title = candidate.title;
        mention.category = candidate.category;
        renderPassage();
        renderIndex();
        persistHistoryAnalysis().catch(error => toast(error.message));
        loadCard(candidate.id);
      });
      view.append(button);
    }
  } else loadCard(mention.id);
}

async function loadCard(id) {
  const sequence = ++state.requestSequence;
  state.card = null;
  const view = $("#card-view");
  view.replaceChildren();
  const loading = element("div", "loading-view");
  loading.append(element("div", "skeleton title"), element("div", "skeleton"), element("div", "skeleton"), element("p", "small", "Finding the explanation and its sources…"));
  view.append(loading);
  try {
    let result = state.cards.get(id);
    if (result) updateUsage({}, { origin: "cache" });
    else {
      result = await api(`/api/card?id=${encodeURIComponent(id)}`);
      state.cards.set(id, result);
      updateUsage({}, result.retrieval);
    }
    if (sequence !== state.requestSequence) return;
    state.card = result.card;
    renderCard();
    persistHistoryCard(result.card).catch(error => toast(error.message));
  } catch (error) {
    if (sequence !== state.requestSequence) return;
    view.replaceChildren(element("h3", "card-title", "Let's try again."), element("p", "card-definition", error.message));
    const button = element("button", "button", "Retry lookup");
    button.addEventListener("click", () => loadCard(id));
    view.append(button);
  }
}

function renderTabs() {
  $$(".tab").forEach(button => {
    const active = button.dataset.tab === state.tab;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
  });
  $("#card-view").setAttribute("aria-labelledby", "tab-" + state.tab);
}

function renderCard() {
  renderTabs();
  const view = $("#card-view");
  view.replaceChildren();
  const card = state.card;
  if (!card) {
    const empty = element("div", "empty-view");
    empty.append(element("span", "empty-icon", "◎"), element("h3", "", "Every word opens a window."), element("p", "", "Choose a highlighted phrase from your reading, or search for a place or concept above."));
    view.append(empty);
    return;
  }
  view.append(element("span", "card-category", card.category));
  const heading = element("div", "card-heading");
  heading.append(element("h3", "card-title", card.title));
  const star = element("button", "star-button");
  star.id = "star-concept";
  setStarState(star, card);
  star.addEventListener("click", () => toggleStar(card, star));
  heading.append(star);
  view.append(heading);
  const mention = state.mentions[state.selectedMention];
  if (mention?.kind === "inferred" && mention.id === card.id) view.append(element("p", "example-box", "Possible connection suggested by AI. This concept is not explicitly named in your passage."));
  if (state.tab === "learn") renderLearn(view, card);
  if (state.tab === "map") renderLocate(view, card);
  if (state.tab === "connect") renderConnect(view, card);
  appendSources(view, card);
}

function renderLearn(view, card) {
  view.append(element("p", "card-definition" + (card.definition.length > 600 ? " long" : ""), card.definition));
  view.append(element("p", "small muted", card.excerpt_label || "Source-derived geographical record"));
  if (card.features.length) {
    view.append(element("h4", "section-label", "What to remember"));
    const list = element("ul", "feature-list");
    card.features.forEach(text => list.append(element("li", "", text)));
    view.append(list);
  }
  if (card.examples.length) {
    view.append(element("h4", "section-label", "See it in the real world"), element("div", "example-box", card.examples.join(" · ")));
  }
  if (card.facts.length) {
    const grid = element("div", "facts-grid");
    card.facts.forEach(fact => {
      const node = element("div", "fact");
      node.append(element("small", "", fact.label), element("strong", "", fact.value));
      grid.append(node);
    });
    view.append(grid);
  }
  if (card.relations.length) {
    view.append(element("h4", "section-label", "Keep connecting"));
    const list = element("div", "related-list");
    card.relations.forEach(relation => list.append(relatedButton(relation)));
    view.append(list);
  }
  if (card.question) appendQuiz(view, card);
  if (card.location) {
    view.append(element("h4", "section-label", "Put it on the map"));
    appendMap(view, card);
  }
}

function relatedButton(relation) {
  const button = element("button", "related-button");
  button.append(element("small", "", relation.label), document.createTextNode(relation.title + " ↗"));
  button.addEventListener("click", () => {
    activateMention(null);
    loadCard(relation.id);
  });
  return button;
}

function renderConnect(view, card) {
  view.append(element("p", "connection-intro", "Build a mental map: follow a relationship to explore the next idea. These connections come from the study guide and linked source, rather than word co-occurrence."));
  view.append(element("div", "connection-center", card.title));
  if (!card.relations.length) view.append(element("p", "card-definition", "No reviewed relationships are available for this entry yet. Explore another highlighted concept in your reading."));
  card.relations.forEach(relation => {
    const row = element("div", "connection-row");
    row.append(element("span", "relation-label", relation.label + " →"), relatedButton(relation));
    view.append(row);
  });
}

function renderLocate(view, card) {
  if (!card.location) {
    view.append(element("p", "card-definition", "This is a geographical idea rather than a single location. Explore its examples or follow a related place in your reading."));
    if (card.examples.length) view.append(element("div", "example-box", "Example regions: " + card.examples.join(" · ")));
    return;
  }
  view.append(element("p", "card-definition", "Start with the world view, then zoom in or open an external map to explore the landscape."));
  appendMap(view, card);
  const links = element("div", "map-links");
  links.append(safeLink("OpenStreetMap ↗", card.location.osm_url, "button"), safeLink("Explore in Google Earth ↗", card.location.earth_url, "button"));
  view.append(links);
}

const SVG = "http://www.w3.org/2000/svg";
function svgElement(tag, attributes) {
  const node = document.createElementNS(SVG, tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  return node;
}

function polygonPath(geometry) {
  const polygons = geometry.type === "Polygon" ? [geometry.coordinates] : geometry.type === "MultiPolygon" ? geometry.coordinates : [];
  return polygons.map(polygon => polygon.map(ring => ring.map(([lon, lat], index) => `${index ? "L" : "M"}${(lon + 180) * 2},${(90 - lat) * 2}`).join(" ") + "Z").join(" ")).join(" ");
}

function appendMap(view, card) {
  const location = card.location;
  const box = element("div", "map-box");
  const map = svgElement("svg", { viewBox: "0 0 720 360", role: "img", "aria-label": `World map showing ${card.title}`, class: "world-map" });
  if (state.world) {
    const grid = svgElement("path", { d: "M0 180H720M360 0V360M0 120H720M0 240H720M180 0V360M540 0V360", class: "map-grid" });
    map.append(grid);
    for (const feature of state.world.features) {
      const selected = feature.properties.ADM0_A3 === location.geometry_code;
      const path = svgElement("path", { d: polygonPath(feature.geometry), class: "map-land" + (selected ? " selected" : "") });
      const title = svgElement("title", {});
      title.textContent = feature.properties.ADMIN;
      path.append(title);
      map.append(path);
    }
    map.append(svgElement("circle", { cx: (location.lon + 180) * 2, cy: (90 - location.lat) * 2, r: 4, class: "map-marker" }));
  } else {
    const text = svgElement("text", { x: 360, y: 180, "text-anchor": "middle", fill: "#61725f", "font-size": 14 });
    text.textContent = "World map unavailable. Use the external map links.";
    map.append(text);
  }
  box.append(map);
  let zoom = 1;
  const controls = element("div", "map-controls");
  const changeZoom = () => {
    const width = 720 / zoom, height = 360 / zoom;
    const cx = (location.lon + 180) * 2, cy = (90 - location.lat) * 2;
    const x = Math.max(0, Math.min(720 - width, cx - width / 2));
    const y = Math.max(0, Math.min(360 - height, cy - height / 2));
    map.setAttribute("viewBox", `${x} ${y} ${width} ${height}`);
    map.querySelector(".map-marker")?.setAttribute("r", String(4 / zoom));
  };
  for (const [label, name, operation] of [["−", "Zoom out", () => { zoom = Math.max(1, zoom / 2); }], ["＋", "Zoom in", () => { zoom = Math.min(16, zoom * 2); }], ["World", "Reset world view", () => { zoom = 1; }]]) {
    const button = element("button", "", label);
    button.setAttribute("aria-label", name);
    button.addEventListener("click", () => { operation(); changeZoom(); });
    controls.append(button);
  }
  box.append(controls);
  const attribution = element("div", "map-attribution");
  attribution.append(safeLink("Map data: Natural Earth · public domain ↗", "https://www.naturalearthdata.com/about/"));
  box.append(attribution);
  view.append(box);
  const coordinates = element("div", "coordinate-line");
  coordinates.append(element("span", "", `${Math.abs(location.lat).toFixed(2)}° ${location.lat >= 0 ? "N" : "S"} · ${Math.abs(location.lon).toFixed(2)}° ${location.lon >= 0 ? "E" : "W"}`), element("span", "", location.kind));
  view.append(coordinates);
  view.append(element("p", "small muted", location.geometry_code ? "Highlighted boundaries use Natural Earth's representation. The marker is a representative point." : "The marker represents a location, not the full extent of the feature."));
}

function appendSources(view, card) {
  const sources = element("div", "source-list");
  sources.append(element("p", "source-label", "FOLLOW THE EVIDENCE"));
  for (const source of card.sources) {
    const row = element("div", "source-item");
    row.append(safeLink(source.title + " ↗", source.url));
    const date = source.retrieved_at ? new Date(source.retrieved_at).toISOString().slice(0, 10) : "";
    row.append(element("small", "", [source.license, date ? `Snapshot: ${date}` : "", source.revision ? `Revision: ${source.revision}` : ""].filter(Boolean).join(" · ")));
    if (source.revision && /^\d+$/.test(source.revision) && source.url.includes("en.wikipedia.org")) row.append(safeLink("View cited revision ↗", `https://en.wikipedia.org/w/index.php?oldid=${source.revision}`));
    sources.append(row);
  }
  if (card.excerpt && card.excerpt !== card.definition) {
    const details = element("details", "excerpt");
    details.append(element("summary", "", "Read the source excerpt"), element("p", "", card.excerpt));
    sources.append(details);
  }
  view.append(sources);
}

function appendQuiz(view, card) {
  const quiz = element("section", "quiz-box");
  quiz.append(element("h4", "section-label", "A quick check"), element("p", "quiz-prompt", card.question.prompt));
  const feedback = element("p", "quiz-feedback");
  const previous = state.quiz.get(card.id);
  const buttons = card.question.options.map((option, index) => {
    const button = element("button", "quiz-option", `${String.fromCharCode(65 + index)}. ${option}`);
    button.addEventListener("click", async () => {
      buttons.forEach(b => { b.disabled = true; });
      try {
        const result = await api(`/api/quiz?id=${encodeURIComponent(card.id)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ answer: index }) });
        state.quiz.set(card.id, { selected: index, ...result });
        markQuiz(buttons, feedback, state.quiz.get(card.id));
      } catch (error) {
        feedback.textContent = error.message;
        buttons.forEach(b => { b.disabled = false; });
      }
    });
    quiz.append(button);
    return button;
  });
  quiz.append(feedback);
  if (previous) markQuiz(buttons, feedback, previous);
  view.append(quiz);
}

function markQuiz(buttons, feedback, result) {
  buttons.forEach((button, index) => {
    button.disabled = true;
    button.classList.toggle("correct", index === result.answer);
    button.classList.toggle("incorrect", index === result.selected && !result.correct);
  });
  feedback.textContent = `${result.correct ? "That's right. " : "Keep exploring. "}${result.feedback}`;
}

function openMaterial() {
  $("#material-text").value = state.text;
  $("#material-title").value = state.title;
  $("#material-error").hidden = true;
  updateInputCount();
  $("#material-dialog").showModal();
  refreshStatus().catch(() => {
    $("#ai-notice").textContent = "Could not check AI availability. Close and reopen this window to try again.";
  });
}

function updateInputCount() {
  const value = $("#material-text").value.trim();
  $("#input-count").textContent = `${value ? value.split(/\s+/).length.toLocaleString() : 0} words`;
}

async function readFile(file) {
  const error = $("#material-error");
  try {
    if (!file || !file.name.toLowerCase().endsWith(".txt")) throw new Error("Please choose a UTF-8 .txt file.");
    if (file.size > 1_000_000) throw new Error("The file must be no larger than 1 MB.");
    const content = new TextDecoder("utf-8", { fatal: true, ignoreBOM: false }).decode(await file.arrayBuffer());
    $("#material-text").value = content;
    $("#material-title").value = file.name.replace(/\.txt$/i, "");
    updateInputCount();
    error.hidden = true;
  } catch (e) {
    error.textContent = e instanceof TypeError ? "This file is not valid UTF-8. Save it as UTF-8 text and try again." : e.message;
    error.hidden = false;
  } finally { $("#material-file").value = ""; }
}

async function analyze(text, title, sample = false, useAI = false) {
  const result = await api("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, use_ai: useAI, session_id: state.session }) });
  state.requestSequence++;
  state.historyId = null;
  state.analysis = structuredClone(result);
  let historyWarning = "";
  if (!sample) {
    try {
      const entry = { id: crypto.randomUUID(), title: title || text.trim().split("\n")[0].slice(0, 100), text, analysis: structuredClone(result), useAI, createdAt: Date.now(), cards: {} };
      await personalStore.put("history", entry);
      state.historyId = entry.id;
      personalChanged();
    } catch (error) { historyWarning = "History was not saved. " + error.message; toast(historyWarning); }
  }
  state.text = text;
  state.title = title;
  state.mentions = result.mentions;
  state.selectedMention = null;
  state.card = null;
  state.tab = "learn";
  $("#document-label").textContent = sample ? "SAMPLE LESSON" : (title || "YOUR MATERIAL").toUpperCase();
  $("#word-count").textContent = `${result.word_count.toLocaleString()} words · ${result.mentions.length} highlights`;
  $("#reading-status").textContent = [...result.warnings, historyWarning].filter(Boolean).join(" ") || (result.mentions.length ? "" : "No concepts found in the local collection. Try the library search or optional AI assistance.");
  updateUsage(result.usage);
  renderPassage();
  renderIndex();
  renderCard();
  const first = state.mentions.findIndex(m => m.id);
  if (first >= 0) {
    // Start with the lesson's central idea where present.
    const central = state.mentions.findIndex(m => m.id === "wiki:Oceanic climate");
    selectMention(central >= 0 ? central : first);
  }
}

const personalChannel = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel("atlas-personal-change") : null;

function personalChanged() {
  personalChannel?.postMessage("changed");
  return refreshPersonalCounts().catch(error => toast(error.message));
}

async function refreshPersonalCounts() {
  const [historyCount, saved] = await Promise.all([personalStore.count("history"), personalStore.list("saved")]);
  $("#history-count").textContent = historyCount;
  $("#saved-count").textContent = saved.length;
  state.savedIds = new Set(saved.map(entry => entry.id));
  const star = $("#star-concept");
  if (star && state.card) setStarState(star, state.card);
}

personalChannel?.addEventListener("message", () => {
  refreshPersonalCounts().catch(() => {});
  if ($("#collection-dialog").open) renderCollection();
});

function setStarState(button, card) {
  const saved = state.savedIds.has(card.id);
  button.textContent = saved ? "★" : "☆";
  button.classList.toggle("starred", saved);
  button.setAttribute("aria-pressed", String(saved));
  button.setAttribute("aria-label", `${saved ? "Unsave" : "Save"} ${card.title}`);
  button.title = saved ? "Remove from Saved" : "Save explanation to your notebook";
}

async function toggleStar(card, button) {
  button.disabled = true;
  try {
    const existing = await personalStore.get("saved", card.id);
    if (existing) {
      await personalStore.delete("saved", card.id);
      state.savedIds.delete(card.id);
      toast("Removed from your notebook.");
    } else {
      const mention = state.mentions[state.selectedMention];
      const entry = { id: card.id, card: structuredClone(card), keyword: mention?.id === card.id ? mention.text : card.title, lesson: state.historyId ? state.title : "", createdAt: Date.now(), note: "" };
      await personalStore.put("saved", entry);
      state.savedIds.add(card.id);
      toast("Saved to your notebook.");
    }
    setStarState(button, card);
    await personalChanged();
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; }
}

async function persistHistoryAnalysis() {
  if (!state.historyId || !state.analysis) return;
  const id = state.historyId;
  const analysis = structuredClone({ ...state.analysis, mentions: state.mentions });
  await personalStore.update("history", id, entry => entry ? { ...entry, analysis } : undefined);
}

async function persistHistoryCard(card) {
  if (!state.historyId || !state.mentions.some(mention => mention.id === card.id)) return;
  const id = state.historyId;
  const snapshot = structuredClone(card);
  await personalStore.update("history", id, entry => entry ? { ...entry, lastCardId: card.id, cards: { ...entry.cards, [card.id]: snapshot } } : undefined);
}

function openCollection(kind) {
  state.collection = kind;
  const history = kind === "history";
  $("#collection-title").textContent = history ? "Your reading history." : "Your geography notebook.";
  $("#collection-eyebrow").textContent = history ? "YOUR LEARNING JOURNEY" : "IDEAS WORTH KEEPING";
  $("#collection-description").textContent = history
    ? "Pick up where you left off. Your passages and analyses are saved on this browser; reopening them does not repeat AI analysis."
    : "A little collection of places and ideas. Star any explanation to keep its description and sources, then add your own notes.";
  $("#collection-search").value = "";
  $("#collection-search").placeholder = history ? "Search your history…" : "Search saved concepts and notes…";
  $("#clear-collection").textContent = history ? "Clear history" : "Clear saved";
  $("#collection-dialog").showModal();
  renderCollection();
}

async function renderCollection() {
  const sequence = ++state.collectionSequence;
  const kind = state.collection;
  const list = $("#collection-list");
  const status = $("#collection-status");
  status.textContent = "Loading your collection…";
  try {
    const entries = await personalStore.list(kind);
    if (sequence !== state.collectionSequence || kind !== state.collection) return;
    const query = $("#collection-search").value.trim().toLocaleLowerCase();
    const visible = entries.filter(entry => (kind === "history" ? `${entry.title} ${entry.text}` : `${entry.card.title} ${entry.keyword} ${entry.card.definition} ${entry.note}`).toLocaleLowerCase().includes(query));
    status.textContent = `${visible.length} of ${entries.length} ${kind === "history" ? "readings" : "saved concepts"} · stored on this browser`;
    $("#clear-collection").disabled = entries.length === 0;
    list.replaceChildren();
    if (!visible.length) {
      const empty = element("div", "empty-view collection-empty");
      empty.append(element("span", "empty-icon", kind === "history" ? "↶" : "☆"), element("h3", "", query ? "No matches yet." : kind === "history" ? "Your next chapter starts here." : "Keep a little knowledge."), element("p", "", query ? "Try a different word or clear the search." : kind === "history" ? "Upload or paste a passage to save its analysis here. The sample lesson is not added to History." : "Select a highlighted concept, then click the star beside its title to save the explanation."));
      list.append(empty);
      return;
    }
    for (const entry of visible) {
      const row = element("article", "collection-entry");
      const open = element("button", "collection-open");
      open.setAttribute("aria-label", `Open ${kind === "history" ? entry.title : entry.card.title}`);
      const heading = element("span", "collection-entry-title", kind === "history" ? entry.title : entry.card.title);
      const date = new Date(entry.createdAt).toLocaleString("en", { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
      open.append(heading, element("span", "collection-meta", kind === "history" ? `${date} · ${entry.analysis.word_count} words · ${entry.analysis.mentions.length} highlights${entry.useAI ? " · AI assisted" : ""}` : `${entry.card.category} · saved ${date}`), element("span", "collection-preview", kind === "history" ? entry.text.trim().slice(0, 180) : entry.card.definition.slice(0, 200)));
      if (kind === "saved" && entry.note) open.append(element("span", "collection-note", entry.note.slice(0, 180)));
      open.addEventListener("click", () => kind === "history" ? restoreHistory(entry.id) : openSaved(entry.id));
      row.append(open);
      const actions = element("div", "collection-entry-actions");
      if (kind === "saved") {
        const note = element("button", "text-button", entry.note ? "Edit note" : "Add note");
        note.setAttribute("aria-label", `${entry.note ? "Edit" : "Add"} note for ${entry.card.title}`);
        note.addEventListener("click", () => openNote(entry.id));
        actions.append(note);
      }
      const remove = element("button", "text-button danger-button", kind === "history" ? "Delete" : "Remove");
      remove.setAttribute("aria-label", `${kind === "history" ? "Delete" : "Remove"} ${kind === "history" ? entry.title : entry.card.title}`);
      remove.addEventListener("click", () => requestDelete(kind, entry.id, kind === "history" ? entry.title : entry.card.title));
      actions.append(remove);
      row.append(actions);
      list.append(row);
    }
  } catch (error) {
    if (sequence !== state.collectionSequence) return;
    status.textContent = error.message;
    list.replaceChildren();
  }
}

async function restoreHistory(id) {
  try {
    const entry = await personalStore.get("history", id);
    if (!entry) { await renderCollection(); return; }
    state.requestSequence++;
    state.historyId = entry.id;
    state.text = entry.text;
    state.title = entry.title;
    state.analysis = structuredClone(entry.analysis);
    state.mentions = structuredClone(entry.analysis.mentions);
    state.selectedMention = null;
    state.card = null;
    state.tab = "learn";
    for (const [cardId, card] of Object.entries(entry.cards || {})) state.cards.set(cardId, { card, retrieval: { origin: "history", tool_requests: 0, model_calls: 0 } });
    $("#document-label").textContent = entry.title.toUpperCase();
    $("#word-count").textContent = `${entry.analysis.word_count.toLocaleString()} words · ${entry.analysis.mentions.length} highlights`;
    $("#reading-status").textContent = ["Restored from History — no new AI analysis.", ...entry.analysis.warnings].join(" ");
    renderPassage(); renderIndex(); renderCard();
    $("#collection-dialog").close();
    const previous = state.mentions.findIndex(mention => mention.id === entry.lastCardId);
    const first = previous >= 0 ? previous : state.mentions.findIndex(mention => mention.id);
    if (first >= 0) selectMention(first);
    $("#passage").focus();
  } catch (error) { toast(error.message); }
}

async function openSaved(id) {
  try {
    const entry = await personalStore.get("saved", id);
    if (!entry) { await renderCollection(); return; }
    state.requestSequence++;
    activateMention(null);
    state.card = structuredClone(entry.card);
    state.tab = "learn";
    renderCard();
    $("#collection-dialog").close();
    $("#star-concept").focus();
    $("#card-view").scrollIntoView({ block: "nearest" });
  } catch (error) { toast(error.message); }
}

async function openNote(id) {
  try {
    const entry = await personalStore.get("saved", id);
    if (!entry) { await renderCollection(); return; }
    state.noteId = id;
    $("#note-title").textContent = entry.card.title;
    $("#note-definition").textContent = entry.card.definition;
    $("#personal-note").value = entry.note || "";
    $("#note-error").hidden = true;
    $("#note-dialog").showModal();
  } catch (error) { toast(error.message); }
}

function requestDelete(kind, id, title) {
  state.pendingDelete = { kind, id };
  $("#delete-title").textContent = id ? `Delete “${title}”?` : `Clear ${kind === "history" ? "all history" : "all saved concepts"}?`;
  $("#delete-description").textContent = kind === "history"
    ? "This removes the stored reading and analysis from this browser. Your saved concepts are kept. This cannot be undone."
    : "This removes the saved explanation and its personal note from this browser. Your reading history is kept. This cannot be undone.";
  $("#delete-error").hidden = true;
  $("#delete-dialog").showModal();
}

$("#history-button").addEventListener("click", () => openCollection("history"));
$("#saved-button").addEventListener("click", () => openCollection("saved"));
$("#collection-search").addEventListener("input", renderCollection);
$("#clear-collection").addEventListener("click", () => requestDelete(state.collection, null, ""));
$("#cancel-delete").addEventListener("click", () => $("#delete-dialog").close());
$("#confirm-delete").addEventListener("click", async event => {
  const pending = state.pendingDelete;
  if (!pending) return;
  event.target.disabled = true;
  try {
    if (pending.id) await personalStore.delete(pending.kind, pending.id);
    else await personalStore.clear(pending.kind);
    if (pending.kind === "history" && (!pending.id || pending.id === state.historyId)) state.historyId = null;
    $("#delete-dialog").close();
    state.pendingDelete = null;
    await personalChanged();
    await renderCollection();
  } catch (error) { $("#delete-error").textContent = error.message; $("#delete-error").hidden = false; }
  finally { event.target.disabled = false; }
});
$("#save-note").addEventListener("click", async event => {
  event.target.disabled = true;
  try {
    const note = $("#personal-note").value;
    const entry = await personalStore.update("saved", state.noteId, previous => previous ? { ...previous, note } : undefined);
    if (!entry) throw new Error("This saved concept was removed in another tab. Close the editor and save the concept again.");
    $("#note-dialog").close();
    await personalChanged();
    await renderCollection();
    toast("Note saved.");
  } catch (error) { $("#note-error").textContent = error.message; $("#note-error").hidden = false; }
  finally { event.target.disabled = false; }
});

async function loadSample() {
  const sample = await api("/api/sample");
  await analyze(sample.text, sample.title, true);
}

let searchTimer;
$("#concept-search").addEventListener("input", () => {
  clearTimeout(searchTimer);
  state.searchSequence++;
  state.searchController?.abort();
  searchTimer = setTimeout(searchLibrary, 200);
});

async function searchLibrary() {
  const query = $("#concept-search").value.trim();
  const results = $("#search-results");
  if (query.length < 2) { results.hidden = true; return; }
  const sequence = state.searchSequence;
  const controller = new AbortController();
  state.searchController = controller;
  results.replaceChildren(element("p", "search-empty", "Searching the library…"));
  results.hidden = false;
  try {
    const payload = await api(`/api/search?q=${encodeURIComponent(query)}`, { signal: controller.signal });
    if (sequence !== state.searchSequence) return;
    results.replaceChildren();
    payload.results.forEach(item => {
      const button = element("button", "search-result", item.title);
      button.append(element("small", "", item.category));
      button.addEventListener("click", () => {
        results.hidden = true;
        $("#concept-search").value = "";
        activateMention(null);
        state.tab = "learn";
        renderTabs();
        loadCard(item.id);
      });
      results.append(button);
    });
    if (!payload.results.length) results.append(element("p", "search-empty", "No local entry found. Use a specific geographical term."));
    if (state.status.online_enabled) {
      const lookup = element("button", "search-result", `Look up “${query}” in Wikipedia ↗`);
      lookup.addEventListener("click", () => {
        results.hidden = true;
        activateMention(null);
        state.tab = "learn";
        renderTabs();
        loadCard("remote:" + query);
      });
      results.append(lookup);
    }
  } catch (error) {
    if (error.name !== "AbortError" && sequence === state.searchSequence) results.replaceChildren(element("p", "search-empty", error.message));
  }
}

document.addEventListener("click", event => {
  if (!event.target.closest(".search-wrap")) $("#search-results").hidden = true;
});
$("#concept-search").addEventListener("keydown", event => {
  if (event.key === "Escape") $("#search-results").hidden = true;
  if (event.key === "ArrowDown") { event.preventDefault(); $("#search-results button")?.focus(); }
});
$("#search-results").addEventListener("keydown", event => {
  const buttons = $$("button", $("#search-results"));
  const index = buttons.indexOf(document.activeElement);
  if (event.key === "ArrowDown" || event.key === "ArrowUp") {
    event.preventDefault();
    buttons[(index + (event.key === "ArrowDown" ? 1 : -1) + buttons.length) % buttons.length]?.focus();
  }
  if (event.key === "Escape") { $("#search-results").hidden = true; $("#concept-search").focus(); }
});
$$("[data-filter]").forEach(button => button.addEventListener("click", () => {
  state.filter = button.dataset.filter;
  $$("[data-filter]").forEach(b => { b.classList.toggle("active", b === button); b.setAttribute("aria-pressed", String(b === button)); });
  renderPassage();
}));
$("#show-highlights").addEventListener("change", event => { state.highlights = event.target.checked; renderPassage(); });
$$(".tab").forEach(button => {
  button.addEventListener("click", () => { state.tab = button.dataset.tab; renderCard(); });
  button.addEventListener("keydown", event => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const tabs = $$(".tab");
    const index = tabs.indexOf(button);
    const target = event.key === "Home" ? tabs[0] : event.key === "End" ? tabs[2] : tabs[(index + (event.key === "ArrowRight" ? 1 : 2)) % 3];
    target.click(); target.focus();
  });
});
$("#new-material").addEventListener("click", openMaterial);
$("#edit-material").addEventListener("click", openMaterial);
$("#privacy-button").addEventListener("click", () => $("#privacy-dialog").showModal());
$$(".close-dialog").forEach(button => button.addEventListener("click", () => button.closest("dialog").close()));
$("#material-text").addEventListener("input", updateInputCount);
$("#material-file").addEventListener("change", event => readFile(event.target.files[0]));
const drop = $("#drop-zone");
drop.addEventListener("dragover", event => { event.preventDefault(); drop.classList.add("dragging"); });
drop.addEventListener("dragleave", () => drop.classList.remove("dragging"));
drop.addEventListener("drop", event => { event.preventDefault(); drop.classList.remove("dragging"); readFile(event.dataTransfer.files[0]); });
$("#material-form").addEventListener("submit", async event => {
  event.preventDefault();
  const button = $("#analyze-button");
  const error = $("#material-error");
  button.disabled = true; button.textContent = "Finding your concepts…"; error.hidden = true;
  try {
    await analyze($("#material-text").value, $("#material-title").value.trim(), false, $("#use-ai").checked);
    $("#material-dialog").close();
    toast("Your reading is ready to explore.");
  } catch (e) { error.textContent = e.message; error.hidden = false; }
  finally { button.disabled = false; button.textContent = "Explore this reading →"; }
});
$("#use-sample").addEventListener("click", async event => {
  event.target.disabled = true;
  try { await loadSample(); $("#material-dialog").close(); }
  catch (error) { $("#material-error").textContent = error.message; $("#material-error").hidden = false; }
  finally { event.target.disabled = false; }
});

async function refreshStatus() {
    state.status = await api("/api/status", { cache: "no-store" });
    $("#library-status").textContent = `${state.status.knowledge_count} entries to explore`;
    $("#use-ai").disabled = !state.status.ai_available;
    if (!state.status.ai_available) $("#use-ai").checked = false;
    $("#ai-notice").textContent = state.status.ai_available
      ? "Sends your English text to OpenAI. Suggestions may need checking. Local recognition remains available."
      : "Not configured. The local geography library is ready to use.";
}

window.addEventListener("focus", () => refreshStatus().catch(() => {}));
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) refreshStatus().catch(() => {});
});

async function start() {
  renderCard();
  try {
    await refreshStatus();
    await refreshPersonalCounts().catch(error => toast(error.message));
    fetch("/api/world").then(response => { if (!response.ok) throw new Error("Map unavailable"); return response.json(); }).then(world => {
      state.world = world;
      if (state.card?.location) renderCard();
    }).catch(() => {});
    await loadSample();
  } catch (error) {
    $("#library-status").textContent = "Connection unavailable";
    $("#reading-status").textContent = error.message;
  }
}
start();
