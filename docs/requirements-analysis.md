# Requirements Analysis: Geography Learning Agent
# 需求分析：地理学习辅助 Agent

**Version / 版本:** 0.1 — Initial Draft / 初稿  
**Date / 日期:** 2026-10-08  
**Project Area / 项目领域:** AI in Education / 人工智能教育应用

## 1. Project Overview / 项目概述

The Geography Learning Agent is a web application that helps students understand geography while reading English learning materials. Students upload or paste a passage, and the system identifies and highlights geographical entities, technical terms, and relevant descriptions within the original text.

地理学习辅助 Agent 是一个帮助学生在阅读英语学习材料时理解地理知识的网页应用。学生上传或粘贴课文后，系统识别其中的地理实体、专业术语和相关描述，并在原文中高亮。

Selecting a highlight displays a concise explanation, supporting sources, related concepts, and an appropriate map or external location-viewing link in the right panel. The system combines curated curriculum knowledge, open geographical data, and selective language-model assistance to support understanding, memory, spatial awareness, and concept connections.

点击高亮内容后，右侧展示简明解释、支持来源、相关概念，以及适用情况下的地图或外部位置查看链接。系统结合精选课程知识、开放地理数据和按需调用的语言模型，支持理解、记忆、空间认知和概念联系。

## 2. Language Requirements / 语言要求

| ID | English requirement | 中文翻译 |
|---|---|---|
| LANG-01 | All project documentation must be bilingual, with English followed by its Chinese translation. | 所有项目文档必须采用英中双语，英文后提供对应中文翻译。 |
| LANG-02 | All student-facing navigation, buttons, instructions, loading states, and errors must use English only. | 所有学生界面的导航、按钮、说明、加载状态和错误提示仅使用英语。 |
| LANG-03 | Uploaded and pasted materials must be English. Predominantly non-English input receives an English validation message. | 上传和粘贴材料必须为英语；主要为非英语的输入应收到英语校验提示。 |
| LANG-04 | Explanations, relationship labels, questions, and application-generated map labels must be English. | 解释、关系标签、问题及应用生成的地图标签必须使用英语。 |
| LANG-05 | Accepted text must preserve spelling and punctuation, including proper nouns and occasional non-English place names in English passages. | 已接受文本必须保留拼写和标点，包括英语课文中的专有名词及偶尔出现的非英语地名。 |

Bilingual documentation does not imply a bilingual student interface.

双语文档不代表双语学生界面。

## 3. Target Users and Educational Goals / 目标用户与教育目标

The provisional target is secondary-school students learning geography through English materials. Exact age, English proficiency, and curriculum must be confirmed before production content preparation. Teachers and evaluators are secondary stakeholders; a teacher dashboard is outside the initial scope.

暂定目标用户为通过英语材料学习地理的中学生。正式准备内容前须确定年龄、英语水平和课程体系。教师与评估者为次要相关方；初期不包含教师管理面板。

The application should support understanding unfamiliar terms in context, connecting concepts to locations, distinguishing similar concepts, checking factual evidence, and recalling or applying knowledge.

应用应支持结合上下文理解陌生术语、将概念联系到地点、区分相似概念、查看事实证据，以及回忆或应用知识。

## 4. Scope and Priorities / 范围与优先级

| Priority | English scope | 中文范围 |
|---|---|---|
| Must — MVP | English input, recognition, original-text highlighting, sourced cards, local retrieval, caching, and location links. | 必须：英语输入、识别、原文高亮、附来源卡片、本地检索、缓存及位置链接。 |
| Should — MVP | Related-concept navigation, highlight filters, embedded 2D map, and simple recall questions. | 应优先：相关概念导航、高亮筛选、内嵌二维地图及简单回忆题。 |
| Later | Broader description recognition, concept comparison, visual knowledge network, PDF/DOCX import, optional offline encyclopedia. | 后续：更广泛描述识别、概念比较、知识网络、PDF/DOCX 导入及可选离线百科。 |
| Out of initial scope | OCR, fully offline AI, global imagery hosting, custom 3D globe, school accounts, unrestricted autonomous browsing. | 初期不包含：OCR、完全离线 AI、全球影像托管、自建三维地球、学校账号及不受限制的自主浏览。 |

The MVP accepts pasted text and UTF-8 `.txt` files. Proposed initial limits are 10,000 words and 1 MB per file, subject to prototype testing.

最小可行产品接受粘贴文本和 UTF-8 `.txt` 文件。建议初始上限为 10,000 个单词、每个文件 1 MB，原型测试后调整。

## 5. Main User Journey / 主要用户流程

1. Upload or paste English text; validate it and display the original passage on the left. / 上传或粘贴英语文本；校验并在左侧展示原文。
2. Identify terms, resolve likely meanings, and highlight original spans. / 识别术语、确定可能含义并高亮原文片段。
3. Select a highlight; display a stored card or retrieve evidence to prepare one. / 点击高亮；展示已有卡片或检索证据生成卡片。
4. Read explanations, open sources, explore locations, or follow related concepts while preserving the passage. / 阅读解释、打开来源、探索地点或相关概念，同时保留原文。
5. Answer an available recall question and receive evidence-based feedback. / 回答可用的回忆题并获得基于证据的反馈。

## 6. Functional Requirements / 功能需求

### 6.1 Material Input and Display / 材料输入与展示

**FR-01:** Support pasting and `.txt` upload. Reject empty or unsupported input and provide English size, encoding, and language errors.

支持粘贴和 `.txt` 上传。拒绝空输入或不支持的格式，并提供英语大小、编码和语言错误提示。

**FR-02:** Preserve accepted text and paragraphs. Highlights reference original positions rather than AI-rewritten text.

保留已接受文本和段落。高亮对应原文位置，不使用 AI 改写文本。

### 6.2 Recognition and Highlighting / 识别与高亮

**FR-03:** Recognize countries, cities, major physical features, climate types, landforms, and selected geographical processes. Document and version supported vocabulary.

识别国家、城市、主要自然地理实体、气候类型、地貌及选定地理过程。记录支持词汇并管理版本。

**FR-04:** Combine terminology dictionaries and aliases with selective model assistance for unfamiliar expressions and contextual disambiguation.

结合术语词典、别名，以及针对陌生表达和上下文消歧的按需模型辅助。

**FR-05:** Resolve ambiguity through context, offer candidates, or mark unresolved mentions; never silently choose an arbitrary entity.

通过上下文消歧、提供候选或标记未确定项；不能直接选择任意实体。

**FR-06:** Visually distinguish inferred concepts from explicitly named terms.

在视觉上区分推断概念与明确写出的术语。

**FR-07:** Support mouse and keyboard selection, consistent overlap handling that favours complete meaningful phrases, and highlight hiding or category filtering.

支持鼠标和键盘选择、一致的重叠处理并优先完整有意义短语，以及隐藏高亮或按类别筛选。

### 6.3 Knowledge Cards and Sources / 知识卡片与来源

**FR-08:** Concept cards include an English title, concise definition, key characteristics, examples, and sources. Add related concepts and passage relevance where supported.

概念卡片包含英语标题、简短定义、主要特征、实例和来源；资料支持时增加相关概念与课文联系。

**FR-09:** Place cards identify entity type and location. Country cards include available geographical attributes and population with its reference year. Missing fields remain unavailable.

地点卡片说明实体类别和位置。国家卡片包含可用地理属性及注明年份的人口。缺失字段保持不可用。

**FR-10:** Generate explanations from retrieved or curated evidence. Citations must support associated claims; generic encyclopedia homepages are insufficient.

依据检索或整理的证据生成解释。引用须支持对应陈述，百科首页不能满足要求。

**FR-11:** Retain source title, URL or local identifier, retrieval date, and available revision information. Include observation years for time-sensitive facts. Label AI-adapted explanations separately from excerpts.

保留来源标题、网址或本地标识、检索日期及可用版本信息。时效性事实注明数据年份。区分 AI 改写解释与摘录。

**FR-12:** If evidence is unavailable, state that a verified explanation is unavailable and allow retry or alternate meanings; never fabricate explanations or citations.

证据不可用时说明无法提供已核实解释，并允许重试或选择其他含义；不得编造解释或引用。

### 6.4 Maps and Learning Connections / 地图与学习联系

**FR-13:** Resolved entities with suitable coordinates or geometry offer external map links; add embedded maps where practical. Preserve the reading session when opening links.

具有合适坐标或几何范围的已确定实体提供外部地图链接；条件允许时加入内嵌地图。打开链接时保留阅读会话。

**FR-14:** Distinguish representative points from full geographical extent. Label locations illustrating a concept as examples rather than its complete distribution.

区分代表性坐标点与完整地理范围。概念示例地点标记为实例，而非完整分布。

**FR-15:** Use meaningful relationship labels such as “located in,” “example of,” and “influenced by.” Causality requires evidence, not co-occurrence alone.

使用“位于”“实例属于”“受……影响”等有意义关系标签。因果关系需要证据，不能只凭共同出现。

**FR-16:** Offer short recall or comparison questions for supported concepts, keeping questions and feedback within verified knowledge.

针对支持的概念提供简短回忆题或比较题，题目和反馈限定于已核实知识。

## 7. Recommended Technical Approach / 推荐技术方案

Use a controlled workflow: input validation → dictionary matching → selective AI recognition → entity resolution → highlighting → local retrieval → approved online fallback → explanation card → optional map viewing.

采用受控流程：输入校验 → 词典匹配 → 按需 AI 识别 → 实体匹配与消歧 → 高亮 → 本地检索 → 指定在线来源补充 → 解释卡片 → 可选地图查看。

Models assist language understanding and educational adaptation. The application directly handles database queries, coordinates, caches, and link generation.

模型辅助语言理解和教学改写；应用直接处理数据库查询、坐标、缓存和链接生成。

| Component / 组件 | Recommendation / 推荐方案 | Purpose / 用途 |
|---|---|---|
| Curriculum / 课程知识 | Curated English cards / 精选英语卡片 | Consistent teaching content / 一致教学内容 |
| Entity facts / 实体事实 | Selected Wikidata records / 精选 Wikidata 数据 | IDs, attributes, coordinates, relations / 标识、属性、坐标、关系 |
| Encyclopedia / 百科 | English Wikipedia on demand / 按需英语维基百科 | Supporting explanations and sources / 补充解释和来源 |
| Place names / 地名 | Selected GeoNames records / 精选 GeoNames 数据 | Names, aliases, coordinates / 名称、别名、坐标 |
| Geometry / 几何范围 | Natural Earth where appropriate / 适用时使用 Natural Earth | Boundaries and physical features / 边界及自然地理要素 |
| Storage / 存储 | Local database, initially SQLite / 本地数据库，初期 SQLite | Records, retrieval, caching / 记录、检索、缓存 |
| Maps / 地图 | External links first; optional Leaflet 2D map / 优先外部链接，可选 Leaflet 二维地图 | Spatial exploration / 空间探索 |
| AI / 人工智能 | Structured outputs and bounded tool calls / 结构化输出及受限工具调用 | Recognition, disambiguation, adaptation / 识别、消歧、改写 |

These are recommendations, not completed integrations. Model and map providers remain undecided. A vector database is not required initially.

以上为推荐方案而非已完成集成。模型和地图服务商待定。初期不要求向量数据库。

## 8. Knowledge and Data Requirements / 知识与数据需求

Plan approximately 300–500 core concepts plus entities needed by the selected curriculum, rather than ingesting an entire encyclopedia.

规划约 300–500 个核心概念及所选课程需要的实体，不导入整个百科全书。

Records include stable ID, preferred English name, aliases, category, definition, factual attributes, related concepts and evidence, applicable coordinates or geometry, sources, licences, versions, review status, and educational level.

记录包含稳定标识、英语标准名、别名、类别、定义、事实属性、相关概念和证据、适用坐标或范围、来源、许可、版本、审核状态及学习阶段。

Store text mentions separately from knowledge records so repeated occurrences share a concept while retaining their original positions.

将课文出现位置与知识记录分开保存，使重复词语共享概念，同时保留原文位置。

## 9. Cost, Reliability, and Privacy / 成本、可靠性与隐私

| ID | English requirement | 中文翻译 |
|---|---|---|
| NFR-01 | Analyze a document once per version and reuse results. | 每个文档版本分析一次并复用结果。 |
| NFR-02 | Cache cards by entity, educational level, source version, and explanation version. Exclude private document-specific content from shared caches. | 按实体、学习阶段、来源版本及解释版本缓存；私人文档定制内容不得进入共享缓存。 |
| NFR-03 | Measure model usage, tool requests, cache hits, and estimated session cost. | 统计模型用量、工具请求、缓存命中和会话预估成本。 |
| NFR-04 | Use approved sources, bounded retries, timeouts, and provider limits. | 使用指定来源、有限重试、超时及服务商限额。 |
| NFR-05 | Keep text and available local cards usable during external failures. | 外部失败时保持原文和可用本地卡片可用。 |
| NFR-06 | Treat uploads as untrusted content, not tool-use authorization or system instructions. | 上传材料是不可信内容，不是工具授权或系统指令。 |
| NFR-07 | Do not retain uploads on the server's disk. Save successful readings and their analyses in browser History until the user deletes them; clearly explain local retention and provide deletion controls. | 不在服务端磁盘保留上传材料。成功阅读及分析保存到浏览器历史，保留至用户删除；明确说明本地保留并提供删除操作。 |
| NFR-08 | Explain external model processing in English and transmit minimum necessary text. | 用英语说明外部模型处理，并仅传输必要文本。 |
| NFR-09 | Do not rely solely on colour; provide visible keyboard focus. | 不仅依赖颜色表达，并提供可见键盘焦点。 |

Offline knowledge storage does not imply fully offline AI. Models, missing entries, and external maps may still require networking.

离线知识存储不代表完全离线 AI；模型、缺失条目及外部地图仍可能需要网络。

## 10. Acceptance Criteria / 验收标准

These are proposed prototype targets, measured on an agreed device, network, and dataset.

以下为建议原型目标，须在约定设备、网络和数据集上测量。

| Area / 领域 | English criterion | 中文标准 |
|---|---|---|
| Language / 语言 | Student UI is English; documents are bilingual. | 学生界面为英语，文档为双语。 |
| Fidelity / 原文保留 | Highlighting changes neither text nor paragraph order. | 高亮不改变文本或段落顺序。 |
| Recognition / 识别 | On at least 30 manually annotated held-out passages, explicit-term precision ≥90% and recall ≥85%. | 至少 30 篇人工标注且未用于调优的课文中，明确术语精确率 ≥90%、召回率 ≥85%。 |
| Linking / 实体链接 | Accuracy ≥90% among resolved explicit mentions; report unresolved cases and coverage separately. | 已解析明确词语的链接准确率 ≥90%；分别报告未确定项及覆盖率。 |
| Citations / 引用 | Every factual card has sources; reviewed claims achieve ≥95% source support; correct errors before demonstration. | 每张事实卡片有来源；抽查陈述获得来源支持的比例 ≥95%；演示前修正错误。 |
| Dates / 年份 | Every population value has a reference year. | 每个人口数值注明年份。 |
| Maps / 地图 | Test links open intended places and correctly label representative/example locations. | 测试链接打开正确位置并正确标注代表点或实例。 |
| Cache / 缓存 | Reopening unchanged cached cards triggers no model call. | 重开未变缓存卡片不调用模型。 |
| Performance / 性能 | Proposed p95: cached cards ≤1s, initial 2,000-word analysis ≤20s; online fallback has visible loading and bounded timeout. | 建议第 95 百分位：缓存卡片 ≤1 秒，2,000 词初次分析 ≤20 秒；在线补充显示加载且有超时上限。 |
| Recovery / 恢复 | Simulated model/source failure preserves text and creates no fabricated citations. | 模拟模型或来源失败时保留原文，不编造引用。 |

Evaluate inferred descriptions separately from explicit terms; do not hide their uncertainty in aggregate scores.

分别评估描述推断与明确术语，不用综合分数掩盖推断的不确定性。

## 11. Educational Evaluation / 教育效果评估

Compare standard passage reading, reading with static encyclopedia links, and reading with the agent. Measure immediate comprehension, delayed recall, relationship explanation, transfer to new examples, usability, interaction time, and cost. Report pilot limitations; clicks and reading time alone are not evidence of learning gains.

比较普通阅读、静态百科链接阅读及 Agent 阅读。测量即时理解、延迟记忆、关系解释、新例子迁移、易用性、交互时间和成本。报告试点局限；点击次数和阅读时长本身不证明学习改善。

## 12. Assumptions and Open Decisions / 假设与待确定事项

| Item / 事项 | Assumption / 假设 | Decision / 待定 |
|---|---|---|
| Learners / 学习者 | Secondary school / 中学生 | Age and English level / 年龄及英语水平 |
| Curriculum / 课程 | Introductory geography / 基础地理 | Curriculum and first topics / 课程及首批主题 |
| Deployment / 部署 | Small classroom/research prototype / 小规模课堂或研究原型 | Region and network / 地区及网络 |
| Model / 模型 | Economical structured-output model / 经济型结构化输出模型 | Provider, benchmark, budget / 服务商、测试、预算 |
| Maps / 地图 | Links plus optional 2D map / 链接及可选二维地图 | Provider, attribution, availability / 服务商、署名、可用性 |
| Storage / 存储 | Browser History and Saved; transient server analysis / 浏览器历史与收藏，服务端临时分析 | Research-data policy and future account sync / 研究数据政策及未来账号同步 |

These decisions do not block prototype planning but must be resolved before production deployment or formal student research.

这些决定不阻碍原型规划，但须在正式部署或学生研究前确定。

## 13. Additional Personal-Learning Requirements / 新增个人学习需求

**FR-17 — History:** Provide a History button on the homepage. Save every successfully analyzed uploaded or pasted English passage, its title, time, highlights, ambiguity choices, and viewed explanation snapshots. List entries newest first, support search and deletion, and restore the original analysis without another model call. Do not include the sample or failed analyses. Data persist in the current browser across refresh and server restart.

**FR-17——历史记录：** 主页提供 History 按钮。保存每篇成功分析的英语上传或粘贴材料、标题、时间、高亮、歧义选择及已查看解释快照。按最新优先展示，支持搜索和删除，恢复原有分析时不重复模型调用。不包含示例或失败分析。数据在当前浏览器中跨刷新和服务重启保留。

**FR-18 — Notebook:** Allow every successfully loaded concept card to be starred or unstarred. A Saved button shows unique saved concepts with their description and source snapshot; support opening, searching, personal notes, removal, and clearing. Deleting History must not delete Saved, and vice versa. Storage failures must be reported without discarding the active reading.

**FR-18——笔记本：** 每个成功加载的概念卡片均可星标或取消星标。Saved 按钮展示去重的收藏概念、描述及来源快照；支持打开、搜索、个人笔记、移除及清空。删除历史不删除收藏，反之亦然。存储失败必须提示，不能丢弃当前阅读。

These browser-persistence requirements supersede the initial transient-only document handling assumption. They do not introduce accounts or device synchronization.

这些浏览器持久化需求替代最初仅临时处理文档的假设，不引入账号或设备同步。

## 14. Reference Sources / 参考来源

Integrations must follow applicable licences and current service policies.

集成须遵守适用许可和当前服务政策。

- [Wikidata licensing / Wikidata 许可](https://www.wikidata.org/wiki/Wikidata:Licensing)
- [Wikidata data access / Wikidata 数据访问](https://www.wikidata.org/wiki/Wikidata:Reuse)
- [GeoNames export / GeoNames 导出](https://www.geonames.org/export/)
- [Natural Earth / Natural Earth 数据](https://www.naturalearthdata.com/about/)
- [Kiwix / Kiwix 离线百科](https://kiwix.org/en/)
- [Wikimedia Terms / Wikimedia 使用条款](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use)
- [OpenStreetMap tile policy / OpenStreetMap 瓦片政策](https://operations.osmfoundation.org/policies/tiles/)
