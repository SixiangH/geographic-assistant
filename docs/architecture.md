# Architecture and API
# 架构与 API

## Components / 组件

FastAPI serves both the JSON API and the static English interface. The frontend uses plain JavaScript and CSS without a build system. The local world map is drawn with SVG from Natural Earth GeoJSON, avoiding a tile-service dependency. This replaces the optional Leaflet recommendation for the initial map; external links still provide detailed maps and imagery.

FastAPI 同时提供 JSON API 和英语静态界面。前端使用原生 JavaScript 与 CSS，无需构建系统。本地世界地图根据 Natural Earth GeoJSON 使用 SVG 绘制，避免瓦片服务依赖。这替代了初版可选 Leaflet 方案；外部链接仍可提供详细地图和影像。

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
