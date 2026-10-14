import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/components/ui/native-select";
import {
  Globe2,
  History,
  Bookmark,
  Library,
  Plus,
  X,
  Compass,
  MousePointer2,
  Search,
} from "lucide-react";

// Render the shell once. Agent-owned empty regions are updated by the existing controllers.
// Preserve existing controller ownership of dynamic content.
export default function App() {
  return (
    <>
      <a className={"skip-link"} href={"#passage"}>
        {"Skip to reading material"}
      </a>
      <header className={"app-header"}>
        <a className={"brand"} href={"/"} aria-label={"Atlas home"}>
          <Globe2 aria-hidden="true" size={18} />
          <span>
            {"atlas"}
            <span className={"brand-dot"}>{"."}</span>
          </span>
        </a>
        <Separator orientation="vertical" className="header-separator" />
        <span className={"header-caption"}>
          {"YOUR GEOGRAPHY LEARNING COMPANION"}
        </span>
        <div className={"header-actions"}>
          <span className={"library-status"} id={"library-status"}>
            {"Connecting…"}
          </span>
          <nav className={"personal-nav"} aria-label={"Your learning"}>
            <Button
              className={"nav-button"}
              id={"history-button"}
              variant="ghost"
              type="button"
            >
              <History aria-hidden="true" size={18} />
              {" History "}
              <Badge
                id={"history-count"}
                className={"nav-count"}
                variant="secondary"
              >
                {"0"}
              </Badge>
            </Button>
            <Button
              className={"nav-button"}
              id={"saved-button"}
              variant="ghost"
              type="button"
            >
              <Bookmark aria-hidden="true" size={18} />
              {" Saved "}
              <Badge
                id={"saved-count"}
                className={"nav-count"}
                variant="secondary"
              >
                {"0"}
              </Badge>
            </Button>
            <Button
              className={"nav-button"}
              id={"library-button"}
              variant="ghost"
              type="button"
            >
              <Library aria-hidden="true" size={18} />
              {" Library"}
            </Button>
          </nav>
          <Button
            className={"button primary"}
            id={"new-material"}
            variant="default"
            type="button"
          >
            <Plus aria-hidden="true" size={18} />
            {" New material"}
          </Button>
        </div>
      </header>
      <main>
        <section className={"intro"}>
          <div>
            <p className={"eyebrow"}>{"YOUR READING, IN CONTEXT"}</p>
            <h1>
              {"Read the words. "}
              <span>{"Discover the world."}</span>
            </h1>
          </div>
          <span className={"intro-note"} aria-hidden={"true"}>
            {"Source-backed explanations"}
            <br />
            {"A little curiosity goes a long way."}
          </span>
        </section>
        <section className={"study-toolbar"} aria-label={"Learning mode"}>
          <div>
            <Label htmlFor={"study-mode"}>{"Learning mode"}</Label>
            <NativeSelect id={"study-mode"} defaultValue="guided">
              <NativeSelectOption value={"explore"}>
                {"Explore freely"}
              </NativeSelectOption>
              <NativeSelectOption value={"guided"}>
                {"Guided study"}
              </NativeSelectOption>
            </NativeSelect>
          </div>
          <p id={"study-progress"} role={"status"}>
            {"Read and explore at your own pace."}
          </p>
          <div className={"study-actions"}>
            <Button
              className={"button"}
              id={"study-start"}
              variant="outline"
              type="button"
            >
              {"Start guided study"}
            </Button>
            <Button
              className={"button"}
              id={"study-check"}
              hidden={true}
              variant="outline"
              type="button"
            >
              {"Check my learning"}
            </Button>
            <Button
              className={"text-button"}
              id={"study-results"}
              variant="ghost"
              type="button"
            >
              {"Study results "}
              <span id={"study-due"}></span>
            </Button>
          </div>
          <p
            id={"study-storage-warning"}
            className={"error"}
            role={"alert"}
            hidden={true}
          ></p>
        </section>
        <section
          className={"workspace"}
          aria-label={"Geography learning workspace"}
        >
          <Card
            className={"reading-panel"}
            aria-labelledby={"reading-heading"}
            role="region"
          >
            <div className={"panel-heading"}>
              <div>
                <Badge className={"step-number"} variant="secondary">
                  {"01"}
                </Badge>
                <h2 id={"reading-heading"}>{"Your reading"}</h2>
              </div>
              <Button
                className={"text-button"}
                id={"edit-material"}
                variant="ghost"
                type="button"
              >
                {"Change material ↗"}
              </Button>
            </div>
            <div className={"reading-meta"}>
              <Badge
                className={"tag"}
                id={"document-label"}
                variant="secondary"
              >
                {"SAMPLE LESSON"}
              </Badge>
              <span id={"word-count"}></span>
            </div>
            <div className={"reading-toolbar"}>
              <div
                className={"filter-group"}
                aria-label={"Highlight categories"}
              >
                <Button
                  className={"filter active"}
                  data-filter={"all"}
                  aria-pressed={"true"}
                  variant="ghost"
                  type="button"
                >
                  {"All concepts"}
                </Button>
                <Button
                  className={"filter"}
                  data-filter={"places"}
                  aria-pressed={"false"}
                  variant="ghost"
                  type="button"
                >
                  {"Places"}
                </Button>
                <Button
                  className={"filter"}
                  data-filter={"ideas"}
                  aria-pressed={"false"}
                  variant="ghost"
                  type="button"
                >
                  {"Ideas"}
                </Button>
              </div>
              <Label className={"toggle-label"}>
                <input
                  type={"checkbox"}
                  id={"show-highlights"}
                  defaultChecked={true}
                />
                {" Highlights"}
              </Label>
            </div>
            <div
              id={"reading-status"}
              className={"reading-status"}
              role={"status"}
              aria-live={"polite"}
            >
              {"Preparing your reading…"}
            </div>
            <article
              id={"passage"}
              className={"passage"}
              tabIndex={"-1"}
              aria-label={"Original learning material"}
            ></article>
            <div className={"reading-bottom"}>
              <MousePointer2 aria-hidden="true" size={18} />
              <p>
                {"Select any highlighted phrase to explore it."}
                <br />
                <span>
                  {"Dotted highlights suggest a possible related concept."}
                </span>
              </p>
            </div>
            <details className={"concept-index"}>
              <summary>
                <span>{"In this reading"}</span>
                <span id={"concept-count"}>{"0 concepts"}</span>
              </summary>
              <div id={"concept-list"} className={"concept-list"}></div>
            </details>
          </Card>
          <Card
            className={"explore-panel"}
            aria-labelledby={"explore-heading"}
            role="complementary"
          >
            <div className={"panel-heading"}>
              <div>
                <Badge className={"step-number"} variant="secondary">
                  {"02"}
                </Badge>
                <h2 id={"explore-heading"}>{"Explore a little deeper"}</h2>
              </div>
              <Compass aria-hidden="true" size={18} />
            </div>
            <details className={"material-summary-panel"} open={true}>
              <summary className={"summary-heading"}>
                <h2 id={"summary-heading"}>{"Material summary"}</h2>
                <span className={"summary-chevron"} aria-hidden={"true"}>
                  {"⌄"}
                </span>
              </summary>
              <div className={"summary-content"}>
                <p
                  id={"material-summary"}
                  className={"summary-text"}
                  aria-live={"polite"}
                >
                  {"Your reading summary will appear here."}
                </p>
                <p
                  id={"summary-warning"}
                  className={"summary-warning"}
                  hidden={true}
                ></p>
              </div>
            </details>
            <div className={"search-wrap"}>
              <Label className={"sr-only"} htmlFor={"concept-search"}>
                {"Search the geography library"}
              </Label>
              <Search aria-hidden="true" size={18} />
              <Input
                id={"concept-search"}
                type={"search"}
                placeholder={"Find a place or concept…"}
                autoComplete={"off"}
              />
              <div
                id={"search-results"}
                className={"search-results"}
                hidden={true}
              ></div>
            </div>
            <div
              className={"tabs"}
              role={"tablist"}
              aria-label={"Exploration views"}
            >
              <Button
                id={"tab-learn"}
                className={"tab active"}
                role={"tab"}
                aria-selected={"true"}
                aria-controls={"card-view"}
                data-tab={"learn"}
                variant="ghost"
                type="button"
              >
                {"Learn"}
              </Button>
              <Button
                id={"tab-map"}
                className={"tab"}
                role={"tab"}
                aria-selected={"false"}
                aria-controls={"card-view"}
                data-tab={"map"}
                tabIndex={"-1"}
                variant="ghost"
                type="button"
              >
                {"Locate"}
              </Button>
              <Button
                id={"tab-connect"}
                className={"tab"}
                role={"tab"}
                aria-selected={"false"}
                aria-controls={"card-view"}
                data-tab={"connect"}
                tabIndex={"-1"}
                variant="ghost"
                type="button"
              >
                {"Connect"}
              </Button>
            </div>
            <div
              className={"explorer-navigation"}
              aria-label={"Explorer navigation"}
            >
              <Button
                className={"text-button"}
                id={"back-card"}
                disabled={true}
                variant="ghost"
                type="button"
              >
                {"← Back"}
              </Button>
              <Button
                className={"text-button"}
                id={"back-collection"}
                hidden={true}
                variant="ghost"
                type="button"
              >
                {"Back to Library"}
              </Button>
              <Button
                className={"text-button"}
                id={"back-reading"}
                variant="ghost"
                type="button"
              >
                {"Back to reading ↑"}
              </Button>
            </div>
            <div
              id={"card-view"}
              tabIndex={"-1"}
              className={"card-view"}
              role={"tabpanel"}
              aria-labelledby={"tab-learn"}
              aria-live={"polite"}
            ></div>
          </Card>
        </section>
        <footer className={"app-footer"}>
          <span>{"Made for curious minds. Grounded in real sources."}</span>
          <div>
            <Button
              className={"text-button"}
              id={"privacy-button"}
              variant="ghost"
              type="button"
            >
              {"Privacy & sources"}
            </Button>
            <details className={"usage-details"}>
              <summary>{"Session activity"}</summary>
              <div id={"session-usage"}>
                {"No model calls in this session."}
              </div>
            </details>
          </div>
        </footer>
      </main>
      <dialog id={"material-dialog"} className={"material-dialog"}>
        <form id={"material-form"}>
          <div className={"dialog-heading"}>
            <div>
              <p className={"eyebrow"}>{"START EXPLORING"}</p>
              <h2>{"Bring your own reading."}</h2>
            </div>
            <Button
              className={"icon-button close-dialog"}
              type={"button"}
              aria-label={"Close material dialog"}
              variant="ghost"
            >
              <X aria-hidden="true" size={18} />
            </Button>
          </div>
          <p className={"dialog-description"}>
            {
              "Choose a demo reading, paste an English passage, or upload a UTF-8 text file. Your original words stay intact. AI assistance finds additional concepts and creates a summary of up to 50 words. Guided study adds one call for up to five multiple-choice and true/false questions."
            }
          </p>
          <p className={"small muted"}>
            {
              "Successful analyses are saved to History on this browser. You can delete them at any time."
            }
          </p>
          <div className="demo-material-picker">
            <Label htmlFor="demo-material">Try a demo material</Label>
            <p className="small muted">Choose one of 10 introductory university geography readings. No file download is needed.</p>
            <NativeSelect id="demo-material" className="input" aria-describedby="demo-material-info">
              <NativeSelectOption value="">Choose a reading…</NativeSelectOption>
            </NativeSelect>
            <Button id="load-demo-material" type="button" variant="outline" disabled={true}>Use this material</Button>
            <p id="demo-material-info" className="small muted" role="status" aria-live="polite">The original source credits and licence are included in each reading.</p>
          </div>
          <Label htmlFor={"material-title"}>
            {"Lesson title "}
            <span className={"optional"}>{"(optional)"}</span>
          </Label>
          <Input
            id={"material-title"}
            className={"input"}
            maxLength={"120"}
            placeholder={"e.g. Rivers and the landscapes they shape"}
          />
          <Label htmlFor={"material-text"}>{"Learning material"}</Label>
          <Textarea
            id={"material-text"}
            placeholder={"Paste your English learning material here…"}
            rows={"9"}
          ></Textarea>
          <div id={"drop-zone"} className={"drop-zone"}>
            <span aria-hidden={"true"}>{"↑"}</span>
            <Label htmlFor={"material-file"}>{"Choose a .txt file"}</Label>
            <span>{"or drop it here · UTF-8 · up to 1 MB"}</span>
            <input
              id={"material-file"}
              type={"file"}
              accept={".txt,text/plain"}
              className={"sr-only"}
            />
          </div>
          <div className={"input-meta"}>
            <span id={"input-count"}>{"0 words"}</span>
            <span>{"Up to 10,000 words"}</span>
          </div>
          <Label htmlFor={"material-mode"}>{"Learning mode"}</Label>
          <NativeSelect id={"material-mode"} className={"input"} defaultValue="guided">
            <NativeSelectOption value={"explore"}>
              {"Explore freely"}
            </NativeSelectOption>
            <NativeSelectOption value={"guided"}>
              {"Guided study: read, compare and try a short quiz"}
            </NativeSelectOption>
          </NativeSelect>
          <p className={"small muted"}>
            {
              "Guided study lets you choose unfamiliar concepts, compare your understanding with sourced explanations, and try a short quiz. Your answers stay in this browser."
            }
          </p>
          <Label className={"ai-option"}>
            <input type={"checkbox"} id={"use-ai"} disabled={true} />
            <span>
              <strong>{"Use AI for concepts, summary and a short quiz"}</strong>
              <small id={"ai-notice"}>
                {"Not configured. The local geography library is ready to use."}
              </small>
            </span>
          </Label>
          <p
            id={"material-error"}
            className={"error"}
            role={"alert"}
            hidden={true}
          ></p>
          <div className={"dialog-actions"}>
            <Button
              className={"button primary"}
              type={"submit"}
              id={"analyze-button"}
              variant="default"
            >
              {"Explore this reading "}
              <span aria-hidden={"true"}>{"→"}</span>
            </Button>
          </div>
        </form>
      </dialog>
      <dialog
        id={"collection-dialog"}
        className={"collection-dialog"}
        aria-labelledby={"collection-title"}
      >
        <div className={"dialog-heading"}>
          <div>
            <p className={"eyebrow"} id={"collection-eyebrow"}>
              {"YOUR LEARNING JOURNEY"}
            </p>
            <h2 id={"collection-title"}>{"History"}</h2>
          </div>
          <Button
            className={"icon-button close-dialog"}
            type={"button"}
            aria-label={"Close collection"}
            variant="ghost"
          >
            <X aria-hidden="true" size={18} />
          </Button>
        </div>
        <p className={"dialog-description"} id={"collection-description"}></p>
        <div className={"collection-toolbar"}>
          <Label className={"sr-only"} htmlFor={"collection-search"}>
            {"Search your collection"}
          </Label>
          <Input
            className={"input"}
            type={"search"}
            id={"collection-search"}
            placeholder={"Search your history…"}
          />
          <Button
            className={"text-button danger-button"}
            id={"clear-collection"}
            variant="ghost"
            type="button"
          >
            {"Clear history"}
          </Button>
        </div>
        <p
          id={"collection-status"}
          className={"small muted"}
          role={"status"}
          aria-live={"polite"}
        ></p>
        <div id={"collection-list"} className={"collection-list"}></div>
      </dialog>
      <dialog
        id={"library-dialog"}
        className={"collection-dialog library-dialog"}
        aria-labelledby={"library-title"}
      >
        <div className={"dialog-heading"}>
          <div>
            <p className={"eyebrow"}>{"EXPLORE THE LOCAL COLLECTION"}</p>
            <h2 id={"library-title"}>{"Geography library"}</h2>
          </div>
          <Button
            className={"icon-button close-dialog"}
            type={"button"}
            aria-label={"Close library"}
            variant="ghost"
          >
            <X aria-hidden="true" size={18} />
          </Button>
        </div>
        <p className={"dialog-description"}>
          {
            "Browse every local entry. Select a concept to explore its explanation, sources, maps, and connections."
          }
        </p>
        <div className={"library-controls"}>
          <Label className={"sr-only"} htmlFor={"library-query"}>
            {"Search local knowledge"}
          </Label>
          <Input
            type={"search"}
            className={"input"}
            id={"library-query"}
            maxLength={"120"}
            placeholder={"Search names, aliases, or descriptions…"}
          />
          <Label className={"sr-only"} htmlFor={"library-category"}>
            {"Knowledge category"}
          </Label>
          <NativeSelect className={"input"} id={"library-category"}>
            <NativeSelectOption value={"all"}>
              {"All categories"}
            </NativeSelectOption>
            <NativeSelectOption value={"country"}>
              {"Countries & territories"}
            </NativeSelectOption>
            <NativeSelectOption value={"place"}>
              {"Places & cities"}
            </NativeSelectOption>
            <NativeSelectOption value={"physical"}>
              {"Physical geography"}
            </NativeSelectOption>
            <NativeSelectOption value={"climate"}>
              {"Weather & climate"}
            </NativeSelectOption>
            <NativeSelectOption value={"landform"}>
              {"Landforms & ecosystems"}
            </NativeSelectOption>
            <NativeSelectOption value={"process"}>
              {"Processes & phenomena"}
            </NativeSelectOption>
            <NativeSelectOption value={"concept"}>
              {"Geography concepts"}
            </NativeSelectOption>
            <NativeSelectOption value={"human"}>
              {"Human geography"}
            </NativeSelectOption>
          </NativeSelect>
        </div>
        <p
          id={"library-feedback"}
          className={"small muted"}
          role={"status"}
          aria-live={"polite"}
        ></p>
        <div id={"library-list"} className={"library-list"}></div>
        <div className={"library-pagination"}>
          <Button
            className={"button"}
            id={"library-previous"}
            disabled={true}
            variant="outline"
            type="button"
          >
            {"Previous"}
          </Button>
          <span id={"library-page"}>{"Page 1"}</span>
          <Button
            className={"button"}
            id={"library-next"}
            disabled={true}
            variant="outline"
            type="button"
          >
            {"Next"}
          </Button>
        </div>
      </dialog>
      <dialog
        id={"note-dialog"}
        className={"note-dialog"}
        aria-labelledby={"note-title"}
      >
        <div className={"dialog-heading"}>
          <div>
            <p className={"eyebrow"}>{"YOUR NOTEBOOK"}</p>
            <h2 id={"note-title"}>{"Add a note"}</h2>
          </div>
          <Button
            className={"icon-button close-dialog"}
            type={"button"}
            aria-label={"Close note editor"}
            variant="ghost"
          >
            <X aria-hidden="true" size={18} />
          </Button>
        </div>
        <p id={"note-definition"} className={"card-definition"}></p>
        <Label htmlFor={"personal-note"}>{"Your note"}</Label>
        <Textarea
          id={"personal-note"}
          rows={"5"}
          maxLength={"5000"}
          placeholder={
            "A connection, an example, or something you want to remember…"
          }
        ></Textarea>
        <p className={"small muted"}>
          {"Only saved in this browser. Up to 5,000 characters."}
        </p>
        <p
          id={"note-error"}
          className={"error"}
          role={"alert"}
          hidden={true}
        ></p>
        <div className={"dialog-actions"}>
          <Button
            className={"button primary"}
            id={"save-note"}
            variant="default"
            type="button"
          >
            {"Save note"}
          </Button>
        </div>
      </dialog>
      <dialog
        id={"delete-dialog"}
        className={"delete-dialog"}
        aria-labelledby={"delete-title"}
      >
        <h2 id={"delete-title"}>{"Delete this entry?"}</h2>
        <p id={"delete-description"} className={"dialog-description"}></p>
        <p
          id={"delete-error"}
          className={"error"}
          role={"alert"}
          hidden={true}
        ></p>
        <div className={"dialog-actions"}>
          <Button
            className={"button"}
            id={"cancel-delete"}
            variant="outline"
            type="button"
          >
            {"Cancel"}
          </Button>
          <Button
            className={"button destructive"}
            id={"confirm-delete"}
            variant="destructive"
            type="button"
          >
            {"Delete"}
          </Button>
        </div>
      </dialog>
      <dialog
        id={"study-setup"}
        className={"collection-dialog"}
        aria-labelledby={"study-setup-title"}
      >
        <form id={"study-setup-form"}>
          <div className={"dialog-heading"}>
            <div>
              <p className={"eyebrow"}>{"GUIDED STUDY"}</p>
              <h2 id={"study-setup-title"}>{"Which concepts are unfamiliar?"}</h2>
            </div>
            <Button
              type={"button"}
              className={"icon-button close-dialog"}
              aria-label={"Close study setup"}
              variant="ghost"
            >
              <X aria-hidden="true" size={18} />
            </Button>
          </div>
          <p className={"dialog-description"}>
            {
              "Concepts are listed by how often they appear in this material. Nothing is preselected. Choose only concepts you do not know well, or continue without selecting any. You can change your selection while reading."
            }
          </p>
          <div id={"study-targets"} className={"study-targets"}></div>
          <p
            id={"study-setup-error"}
            className={"error"}
            role={"alert"}
            hidden={true}
          ></p>
          <div className={"dialog-actions"}>
            <Button
              type={"button"}
              className={"text-button"}
              id={"study-cancel-setup"}
              variant="ghost"
            >
              {"Keep reading without selecting"}
            </Button>
            <Button
              className={"button primary"}
              type={"submit"}
              variant="default"
            >
              {"Start reading"}
            </Button>
          </div>
        </form>
      </dialog>
      <dialog id={"privacy-dialog"} className={"privacy-dialog"}>
        <div className={"dialog-heading"}>
          <h2>{"A clear view of your data."}</h2>
          <Button
            className={"icon-button close-dialog"}
            type={"button"}
            aria-label={"Close privacy dialog"}
            variant="ghost"
          >
            <X aria-hidden="true" size={18} />
          </Button>
        </div>
        <h3>{"Your reading & notebook"}</h3>
        <p>
          {
            "Successful uploaded or pasted readings and their analyses are saved in History in this browser. Starred explanations, source snapshots, and personal notes are saved in Saved. They remain after a refresh or server restart. You can delete entries or clear either collection. These collections are not synced between browsers, devices, or browser profiles, and clearing browser site data removes them."
          }
        </p>
        <p>
          {
            "Your passage is sent to the local server for analysis but its full text is not stored on the server's disk. Online explanations are temporarily cached for seven days and are not added to the local library. Saved keeps complete explanation and source snapshots in this browser. Temporary server analysis results expire after 10 minutes or a server restart."
          }
        </p>
        <h3>{"Guided study"}</h3>
        <p>
          {
            "Selected unfamiliar concepts, your understanding, source snapshots, concept completion and quiz answers are saved in this browser, not sent to AI or shared with a teacher. Quiz generation sends only the material to AI. Deleting a History reading removes its linked progress. Previous guided-study records are preserved as archived data."
          }
        </p>
        <h3>{"Optional AI assistance"}</h3>
        <p>
          {
            "If configured and selected, your text is sent to OpenAI for recognition, with storage disabled in the API request. Provider retention policies still apply. AI suggestions are not verified facts. Opening History or Saved does not repeat AI analysis."
          }
        </p>
        <h3>{"Knowledge & maps"}</h3>
        <p>
          {
            "Local cards use attributed Wikipedia excerpts, Natural Earth data, and GeoNames records. Online lookup sends only the requested article name to Wikipedia and may request public Wikidata facts. Public encyclopedia cards are cached for seven days. The world map uses Natural Earth data; external map links open another service."
          }
        </p>
        <p>
          {
            "Natural Earth uses a particular boundary representation and is not a definitive statement about disputed territories. Study guides are adaptations; consult the linked evidence and article history."
          }
        </p>
        <a
          href={"https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use"}
          target={"_blank"}
          rel={"noopener noreferrer"}
        >
          {"Wikipedia content reuse terms ↗"}
        </a>
        <p className={"small muted"}>
          {
            "This is a classroom prototype. The knowledge collection has not completed a formal curriculum review."
          }
        </p>
      </dialog>
      <div id={"toast"} className={"toast"} role={"status"} hidden={true}></div>
    </>
  );
}
