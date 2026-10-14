"use strict";

const library = { page: 1, pages: 1, sequence: 0, controller: null, timer: null };
const libraryLabels = {country: "Countries & territories", place: "Places & cities", physical: "Physical geography",
  climate: "Weather & climate", landform: "Landforms & ecosystems", process: "Processes & phenomena",
  concept: "Geography concepts", human: "Human geography"};

async function browseLibrary() {
  clearTimeout(library.timer);
  const sequence = ++library.sequence;
  library.controller?.abort();
  const controller = new AbortController();
  library.controller = controller;
  const list = $("#library-list");
  list.replaceChildren();
  $("#library-feedback").textContent = "Loading the local library…";
  $("#library-previous").disabled = true;
  $("#library-next").disabled = true;
  list.setAttribute("aria-busy", "true");
  try {
    const params = new URLSearchParams({q: $("#library-query").value.trim(),
      category: $("#library-category").value, page: String(library.page)});
    const payload = await api(`/api/library?${params}`, {signal: controller.signal});
    if (sequence !== library.sequence || !$("#library-dialog").open) return;
    library.page = payload.page;
    library.pages = payload.pages;
    $("#library-feedback").textContent = payload.total
      ? `${payload.total.toLocaleString()} entries · ${payload.library_total.toLocaleString()} in the local library`
      : "No entries match your search. Try another term or category.";
    $("#library-page").textContent = `Page ${payload.page} of ${payload.pages}`;
    $("#library-previous").disabled = payload.page <= 1;
    $("#library-next").disabled = payload.page >= payload.pages;
    for (const option of $("#library-category").options) {
      option.textContent = option.value === "all" ? `All categories (${payload.library_total})`
        : `${libraryLabels[option.value]} (${payload.categories[option.value] || 0})`;
    }
    for (const entry of payload.results) {
      const button = element("button", "collection-open library-entry");
      button.setAttribute("aria-label", `Explore ${entry.title}`);
      button.append(element("span", "collection-entry-title", entry.title),
        element("span", "collection-meta", libraryLabels[entry.category]),
        element("span", "collection-preview", entry.preview + (entry.preview.length === 180 ? "…" : "")));
      if (entry.materials?.length) button.append(element("span", "collection-meta",
        "From: " + entry.materials.map(m => m.title).slice(0, 2).join(" · ")));
      button.addEventListener("click", async () => {
        state.returnTo = "library";
        $("#library-dialog").close();
        activateMention(null);
        state.tab = "learn";
        await loadCard(entry.id);
        $("#card-view").scrollIntoView({block: "nearest"});
        $("#card-view").focus({preventScroll: true});
      });
      list.append(button);
    }
    list.scrollTop = 0;
  } catch (error) {
    if (error.name !== "AbortError" && sequence === library.sequence) {
      $("#library-feedback").textContent = error.message;
      const retry = element("button", "button", "Retry loading library");
      retry.addEventListener("click", browseLibrary);
      list.append(retry);
    }
  } finally {
    if (sequence === library.sequence) list.setAttribute("aria-busy", "false");
  }
}

$("#library-button").addEventListener("click", () => {
  $("#library-dialog").showModal();
  browseLibrary();
  $("#library-query").focus();
});
$("#library-query").addEventListener("input", () => {
  library.page = 1;
  library.sequence++;
  library.controller?.abort();
  clearTimeout(library.timer);
  library.timer = setTimeout(browseLibrary, 200);
});
$("#library-category").addEventListener("change", () => { library.page = 1; browseLibrary(); });
$("#library-previous").addEventListener("click", () => { library.page--; browseLibrary(); });
$("#library-next").addEventListener("click", () => { library.page++; browseLibrary(); });
$("#library-dialog").addEventListener("close", () => {
  clearTimeout(library.timer);
  library.sequence++;
  library.controller?.abort();
});
$("#library-dialog").addEventListener("keydown", event => {
  if (event.key === "Escape") {
    event.preventDefault();
    event.stopPropagation();
    $("#library-dialog").close();
  }
});
