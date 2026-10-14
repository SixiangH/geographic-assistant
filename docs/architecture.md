# Architecture and API
# 架构与 API

## Components / 组件

FastAPI serves both the JSON API and the static English interface. The UI shell now uses React, Vite, Tailwind CSS 4, and official shadcn/ui components. Existing JavaScript controllers retain ownership of recognition, cards, collections, and guided study. The local world map is drawn with SVG from Natural Earth GeoJSON, avoiding a tile-service dependency. This replaces the optional Leaflet recommendation for the initial map; external links still provide detailed maps and imagery. See [frontend integration](frontend-ui.md).

FastAPI 同时提供 JSON API 和英语静态界面。界面框架现采用 React、Vite、Tailwind CSS 4 与官方 shadcn/ui 组件。原有 JavaScript 控制器继续管理识别、知识卡片、个人集合和引导学习。本地世界地图根据 Natural Earth GeoJSON 使用 SVG 绘制，避免瓦片服务依赖。这替代了初版可选 Leaflet 方案；外部链接仍可提供详细地图和影像。详见[前端整合说明](frontend-ui.md)。

`app/config.py` loads server-side environment settings. `app/knowledge.py` loads the attributed JSON seed and persists public online cards in SQLite. `app/recognition.py` validates language and creates non-overlapping original-text spans. `app/providers.py` contains bounded OpenAI extraction and Wikipedia/Wikidata retrieval. `app/main.py` orchestrates these services and strips quiz answers from card responses.

`app/config.py` 加载服务端环境设置。`app/knowledge.py` 加载附来源 JSON 初始数据，并用 SQLite 保存公共在线卡片。`app/recognition.py` 校验语言并生成不重叠原文位置。`app/providers.py` 实现受限 OpenAI 提取及 Wikipedia/Wikidata 检索。`app/main.py` 编排服务，并从卡片响应中移除题目答案。

## Recognition flow / 识别流程

1. Validate bytes, word count, control characters, and predominantly English language. Exact known short terms are accepted despite language-detector uncertainty. / 校验字节、词数、控制字符及主要语言；对已知短术语允许语言检测不确定性。
2. Match longer dictionary aliases before shorter ones; avoid word-substring matches and obvious lower-case place-name collisions. / 优先匹配较长别名，避免单词内部匹配及明显小写地名冲突。
3. Preserve unresolved choices for Georgia, Congo, Amazon, and duplicate aliases. / 对 Georgia、Congo、Amazon 及重复别名保留未确定候选。
4. If explicitly enabled, call the model for exact substrings and candidate article titles. Validate confidence, category, exact presence, and non-overlap. / 明确启用后调用模型提取原文片段与候选条目名；校验置信度、类别、原文存在性及不重叠。
5. Convert Python character positions to UTF-16 offsets for JavaScript. / 将 Python 字符位置转换为 JavaScript UTF-16 位置。
6. Retrieve evidence only when a card is selected. Source-derived excerpts are never presented as independently verified AI reasoning. / 选择卡片时才检索证据；来源摘录不呈现为独立核实的 AI 推理。

The model does not make autonomous browsing decisions or generate citations. The server executes a fixed retrieval workflow against approved Wikipedia and Wikidata endpoints. Online entries have source evidence but their geographical relevance is not independently classified; use specific geographical article names.

模型不自主决定浏览行为，也不生成引用。服务端只对指定 Wikipedia 和 Wikidata 端点执行固定检索流程。在线条目有来源证据，但其地理相关性未独立分类，应使用明确的地理条目名。

## API / 接口

| Method / 方法 | Path / 路径 | Purpose / 用途 |
|---|---|---|
| GET | `/api/status` | Configuration availability and seed count; no secrets / 配置可用性及数据量，不返回密钥 |
| GET | `/api/sample` | English sample passage / 英语示例课文 |
| POST | `/api/analyze` | `text`, `use_ai`, `session_id`; returns spans, warnings, usage / 输入文本、AI 开关、会话标识；返回位置、提示和用量 |
| GET | `/api/search?q=...` | Local title and alias search / 本地标题和别名搜索 |
| GET | `/api/card?id=...` | Local, cached, or online evidence card / 本地、缓存或在线证据卡片 |
| POST | `/api/quiz?id=...` | Submit `{ "answer": 0 }`; receive correctness and explanation / 提交答案下标，返回正误和解释 |
| GET | `/api/world` | Bundled Natural Earth GeoJSON / 内置 Natural Earth GeoJSON |
| GET | `/api/docs` | Interactive API documentation / 交互式 API 文档 |

Card IDs use `wiki:`, `country:`, and `geonames:` for local records. `remote:` requests an English Wikipedia article. Namespace separators, multiple-title separators, and newlines are rejected in online titles. Source URLs are constructed or obtained from approved services, not supplied by uploaded content.

本地卡片标识使用 `wiki:`、`country:`、`geonames:` 前缀。`remote:` 请求英语 Wikipedia 条目。在线标题拒绝命名空间分隔符、多标题分隔符和换行。来源链接由指定服务提供或构造，不由上传内容提供。

## State and protection / 状态与保护

The server never saves uploaded documents to disk. `app/static/personal-store.js` manages the browser IndexedDB database `atlas-personal`, with `history` and `saved` stores. History saves original passages, mention analyses, ambiguity choices, and viewed public-card snapshots; Saved keeps unique card IDs, explanation snapshots, source metadata, and personal notes. Records persist until explicitly removed or browser site data is cleared. There is no cross-device or account synchronization.

服务端不将上传文档保存到磁盘。`app/static/personal-store.js` 管理浏览器 IndexedDB 数据库 `atlas-personal`，包含 `history` 和 `saved` 集合。历史保存原文、词语分析、歧义选择及已查看公共卡片快照；收藏以唯一卡片标识保存解释快照、来源元数据及个人笔记。记录持续保留至用户删除或清除站点数据。不提供跨设备或账号同步。

IndexedDB updates use read/write transactions so asynchronously arriving card snapshots do not overwrite ambiguity changes or recreate deleted entries. A BroadcastChannel refreshes collection counts between tabs. Restoring history does not call `/api/analyze`; saved and snapshotted cards render directly. Previously unviewed historical concepts can still request their card from the server. Storage failures leave the active reading usable and display an error.

IndexedDB 更新使用读写事务，避免异步卡片快照覆盖歧义修改或重建已删除记录。BroadcastChannel 刷新不同标签页的集合数量。恢复历史不调用 `/api/analyze`；收藏和已有快照直接展示。历史中未查看过的概念仍可请求服务端卡片。存储失败时当前阅读仍可使用，并显示错误。

The bounded server analysis cache uses a session identifier, AI mode, and SHA-256 digest; it stores mention results rather than full passages. Session identifiers separate cache entries and do not provide authentication.

有界服务端分析缓存以会话标识、AI 模式及 SHA-256 摘要为键，保存识别结果而非全文。会话标识只隔离缓存，不提供身份认证。

Uploaded text is rendered through text nodes, not interpreted as HTML. Content Security Policy limits script, frame, and connection origins. Secrets remain in the environment. A recognition lock prevents duplicate simultaneous paid calls; it also serializes analyses, so scaling needs a job queue and per-session locking.

上传文本通过文本节点展示，不作为 HTML 解析。内容安全策略限制脚本、框架与连接来源。密钥保留在环境中。识别锁避免重复并发付费调用，也会串行处理分析；扩展规模时需任务队列和会话级锁。

## Extension points / 扩展位置

Extend `scripts/build_knowledge.py` to add source-backed vocabulary, study guides, reviewed relations, and questions. A richer retrieval index can replace the in-memory alias search later. OCR, document import, and model-based explanation adaptation should be added as separate validated stages.

可扩展 `scripts/build_knowledge.py` 增加有来源的词汇、学习解释、审核关系和题目。后续可用更丰富检索索引替换内存别名搜索。OCR、文档导入及模型解释改写应作为独立校验阶段加入。

## Local library browser / 本地知识库浏览

`GET /api/library` accepts `q`, `category`, `page`, and `page_size` (1–60, default 30). It returns local seed summaries, total and category counts, and clamped pagination. Search covers aliases and definitions, with exact titles ranked first. Cached online cards are excluded. `library.js` cancels outdated requests and opens the existing card viewer; browsing makes no AI or external source calls.

`GET /api/library` 接受 `q`、`category`、`page` 与 `page_size`（1–60，默认 30），返回本地初始库摘要、总量、类别数量及限制范围后的分页。搜索覆盖别名与解释，完全匹配标题优先。在线缓存卡片不计入列表。`library.js` 取消过期请求并打开现有卡片区域；浏览不调用 AI 或外部来源。

## Bundled library and online snapshots / 内置知识库与在线快照

The local library contains bundled knowledge only. Analysis no longer retrieves or permanently promotes newly discovered concepts; online cards are retrieved on click and cached for seven days outside Library/search. Legacy learned rows are excluded without deleting existing data. Saved stores a complete card and source snapshot in browser IndexedDB, including online concepts absent from the library, so reopening Saved needs neither the server cache nor a new lookup. Material titles and IDs are no longer attached to online cards.

本地知识库仅包含项目内置条目。分析不再自动检索或永久收录新概念；在线卡片在点击时检索，临时缓存七天，不进入 Library/搜索。旧版 learned 数据不再载入知识库，但不删除既有数据。Saved 在浏览器 IndexedDB 中保存完整卡片与来源快照，包括知识库中没有的在线条目，因此重开收藏不依赖服务端缓存或重新检索。在线卡片不再附加材料标题与标识。

Explorer navigation retains up to 40 previous card snapshots without repeating source/model calls. Return controls reopen the originating collection with the Library query/category/page preserved. The headline uses one upright serif typeface.

探索导航保留最多 40 张之前的卡片快照，返回不重复来源或模型调用。返回按钮重新打开原集合，Library 保留搜索、分类和分页状态。顶部标题统一采用正体衬线字体。

## Material summaries / 材料摘要

Every accepted reading receives an English summary of at most 50 whitespace-separated words, shown inside Explore a little deeper, below its heading. Local mode ranks and extracts up to four key sentences without model calls. Enabling AI requests one additional Responses API call for a coherent summary; failed or incomplete responses fall back to local key sentences, with a visible notice. Word limits are enforced on the server even if a model exceeds them. Long AI inputs use bounded representative excerpts across the passage and are labelled accordingly.

每篇已接受材料都生成不超过 50 个按空白分隔英语单词的摘要，展示于 Explore a little deeper 内的标题下方。本地模式排序并提取最多四个关键句，不调用模型。启用 AI 会增加一次 Responses API 调用以生成连贯梗概；失败或不完整响应回退到本地关键句，并显示提示。即使模型超出要求，服务端也会强制限制词数。较长 AI 输入使用遍布原文的受限代表摘录，并明确标注。

Summary text, type, word count, and warnings are stored inside the analysis snapshot in browser History. Reopening a new history record restores the exact summary without model calls. Older history records without summaries show an unavailable notice and may be re-analyzed. Summaries do not change when browsing other knowledge cards, and original material remains unchanged. AI summary usage is included in session token/call/cost accounting. Sample lessons use local summaries only.

摘要文字、类型、词数和提示随分析快照存入浏览器 History。重新打开新历史记录恢复原摘要，不调用模型。没有摘要的旧记录显示缺失提示，可重新分析。浏览其他知识卡片不改变材料摘要，原文保持完整。AI 摘要用量计入会话 token、调用及费用统计。示例课文仅使用本地摘要。

OpenAI request format reference / OpenAI 请求格式参考：[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).


## Reading layout / 阅读布局

The original passage expands to its full height and scrolls with the page. At widths above 720 px, the explorer stays sticky within the workspace, with viewport-bounded height and an independently scrollable explanation. Selecting a new card resets the explanation scroll position. Both numbered headings align and share a white background. The summary sits below the explorer heading and can be collapsed; long summaries scroll within their own bounded area. At narrower widths the panels stack in normal page flow.

原文按全文高度展开，随页面滚动。宽度超过 720 像素时，探索区域在工作区内保持吸顶，高度受视口限制，解释内容独立滚动。选择新卡片时，解释滚动位置重置到顶部。两侧编号标题对齐并采用白色背景。摘要位于探索标题下方，可收起；较长摘要在自身有限区域内滚动。更窄屏幕上，两栏上下排列，随页面正常滚动。


## Guided study / 引导学习

Guided study adds confirmed targets, prediction and revision, baseline and recall/transfer checks, seven-day review reminders, browser-only learning evidence, provisional self-assessment, and JSON export. Explore freely remains available. See [Guided Study and Learning Evidence](guided-study.md).

引导学习新增目标确认、预测与修订、基线和回忆或迁移检查、七天复习提醒、仅保存在浏览器的学习证据、暂定自评及 JSON 导出。保留自由探索模式，详见上方双语设计文档。
