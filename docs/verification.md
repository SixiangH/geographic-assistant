# Verification Report
# 验证报告

**Date / 日期:** 2026-10-08  
**Environment / 环境:** Windows, Conda `aai`, Python 3.11.16  
**Version / 版本:** 0.1.0

## Completed checks / 已完成检查

All 31 automated backend tests passed. They cover sample recognition, original-text offsets including emoji, longest-phrase matching, ambiguity, non-English and oversized inputs, unsupported control characters, AI configuration and failure fallback, session cache separation, source/cache failures, quiz grading, dated population, maps, and seed integrity.

31 项后端自动测试全部通过，覆盖示例识别、含表情字符的原文位置、最长短语匹配、歧义、非英语与超限输入、不支持的控制字符、AI 配置与失败回退、会话缓存隔离、来源与缓存失败、练习评分、带年份人口、地图及初始数据完整性。

Headless Chrome acceptance checks passed at desktop 1440×1100 and mobile 390×844. They exercise real UI controls: sample reading, highlight filtering/hiding, text preservation, quiz response, country map and zoom, external link construction, pasted material, safe rendering of HTML-like text, ambiguous-name selection, language error feedback, UTF-8 file upload, search, and relationship navigation. No JavaScript page errors were recorded, and the mobile layout had no horizontal overflow.

无头 Chrome 在桌面 1440×1100 和手机 390×844 下验收通过。通过真实界面操作检查示例阅读、高亮筛选与隐藏、原文保留、练习反馈、国家地图与缩放、外部链接构造、粘贴材料、类似 HTML 文本的安全展示、歧义选择、语言错误提示、UTF-8 文件上传、搜索及关系导航。没有记录到 JavaScript 页面错误，手机布局没有横向溢出。

Desktop and mobile screenshots were visually inspected. Python compilation and JavaScript syntax checks passed. Tests currently emit a dependency deprecation warning concerning Starlette's HTTPX test adapter; it does not fail tests or affect runtime behavior in the exercised paths.

已人工检查桌面与手机截图。Python 编译检查及 JavaScript 语法检查通过。当前测试会产生一条关于 Starlette HTTPX 测试适配器的依赖弃用警告，不导致测试失败，也未影响已检查路径的运行行为。

## Live retrieval / 实际在线检索

Actual Wikipedia/Wikidata requests were tested for Berlin and Canberra. Responses supplied article excerpts and source metadata; the Berlin result included a dated population statement. Repeating Canberra retrieval used SQLite cache with zero additional source requests and zero model calls.

已对 Berlin 和 Canberra 执行真实 Wikipedia/Wikidata 请求，返回条目摘录及来源元数据；Berlin 返回带年份人口陈述。再次检索 Canberra 使用 SQLite 缓存，没有新增来源请求或模型调用。

OpenStreetMap and Google Earth destination URLs were verified in the UI. External applications themselves were not tested end to end; availability depends on the student's network and service behavior.

已在界面中验证 OpenStreetMap 和 Google Earth 目标网址。未对外部应用执行完整端到端检查，其可用性取决于学生网络及服务行为。

## Local performance / 本地性能

Thirty uncached local analyses of a 2,000-word passage were measured through the test client. The p95 latency was 35.35 ms; the mean was 41.82 ms, including a slower cold initialization. Local card retrieval p95 was 1.55 ms. No model calls were made. These numbers measure this machine and local backend processing, not browser rendering, network latency, or paid model performance.

通过测试客户端测量了 30 次未命中缓存的 2,000 词本地分析。第 95 百分位延迟为 35.35 毫秒；均值为 41.82 毫秒，包含较慢的冷初始化。本地卡片读取第 95 百分位为 1.55 毫秒。未调用模型。这些数据只衡量当前设备的本地后端处理，不代表浏览器渲染、网络延迟或付费模型性能。

Reproduce with `python -m scripts.benchmark`. Results are saved in `test-results/benchmark.json`.

使用 `python -m scripts.benchmark` 复现。结果保存于 `test-results/benchmark.json`。

## Coverage and limitations / 覆盖与局限

History and notebook browser acceptance checks passed. Verified successful uploads, newest-first listing, full-text search, restoring original text and highlights without analysis requests, persisted ambiguity choices, previously viewed source snapshots, starred-card deduplication, notes with safe text rendering, refresh persistence, cross-tab count updates, deletion cancellation, individual deletion, independent collection clearing, and simulated storage failure. Saved and snapshotted cards were tested with the card endpoint blocked. Desktop and mobile collection screenshots were visually inspected. No paid model calls were made by these checks.

历史与笔记本浏览器验收通过。已验证成功上传、最新优先列表、全文搜索、无分析请求的原文与高亮恢复、歧义选择持久化、已查看来源快照、星标去重、笔记安全文本展示、刷新保留、跨标签页数量更新、取消删除、单条删除、独立清空集合及模拟存储失败。通过阻断卡片接口验证收藏及已有快照仍可展示。已检查桌面和手机集合截图；检查未产生付费模型调用。

Configuration-refresh regression checks also passed: changing AI availability from disabled to enabled updates the checkbox when the material dialog is reopened, preserves the passage, and allows checking/unchecking without making a model call.

配置刷新回归检查也已通过：AI 可用性由禁用变为启用时，重新打开材料窗口会更新复选框、保留原文，并允许勾选和取消，不产生模型调用。

- The seed contains 393 entries: 176 country-category entries, 71 places, 46 physical features/regions, 33 climate entries, 28 landforms, 18 processes, 12 general concepts, and 9 human-geography entries. Six entries have recall questions. / 初始数据包含 393 条：176 条国家类别记录、71 条地点、46 条自然地理实体或区域、33 条气候、28 条地貌、18 条过程、12 条通用概念及 9 条人文地理内容；六条提供回忆题。
- No live OpenAI key was supplied. Structured-output handling, simulated extraction, failures, and caching are tested with mocks; real model accuracy, latency, account compatibility, and billing remain unverified. / 没有提供真实 OpenAI 密钥。结构化输出处理、模拟提取、失败和缓存通过模拟测试；真实模型准确率、延迟、账号兼容性及计费尚未验证。
- No independent, manually annotated 30-passage accuracy benchmark has been completed. The requirements' precision and recall figures remain targets, not measured achievements. / 尚未完成独立人工标注的 30 篇课文准确率评估。需求中的精确率和召回率仍是目标，不是已测量成果。
- Study adaptations and relationships are scientifically motivated but still marked for curriculum/editorial review. No formal claim-to-source audit or student learning study has been completed. / 学习改写与概念关系具有科学依据，但仍需课程与编辑审核。未完成正式陈述来源审计或学生学习效果研究。
- Dictionary matching cannot recognize every geographical description and may have contextual false positives. Ambiguity handling is intentionally conservative. Language detection can reject short unfamiliar English inputs; use a complete sentence. / 词典匹配不能识别所有地理描述，也可能产生上下文误识别。歧义处理较保守。语言检测可能拒绝陌生短英语输入，建议提供完整句子。
- Online cards preserve actual source excerpts but are not independently checked for geographical relevance. Missing fields are omitted; city population is not shown without a reference year. / 在线卡片保留实际来源摘录，但未独立检查地理相关性。缺失字段不展示；城市人口没有统计年份时不展示。
- The application is complete as a local MVP. Authentication, multi-user deployment, OCR, document formats beyond `.txt`, and fully offline AI are later work. / 应用作为本地最小可行产品已完成；身份认证、多用户部署、OCR、`.txt` 以外格式及完全离线 AI 属于后续工作。

## Extended knowledge acceptance / 扩展知识验收

The library expanded from 393 to 711 records with 318 additional topics. Every catalog title is checked for offline coverage. Tests verify plural aliases, longest-phrase matching, sourced explanations, and zero model calls for Forest, Lake, Wetland, Soil erosion, Groundwater, Reforestation, Eutrophication, Coastal erosion, and Sea level rise. Inferred climate descriptions can encompass shorter climate keywords while preserving countries and rejecting partial overlaps.

知识库从 393 条扩充到 711 条，新增 318 个主题。测试检查目录中的每个标题均有离线条目，并验证复数别名、最长短语匹配、附来源解释及上述森林、湖泊、湿地、土壤侵蚀等条目不调用模型。推断气候描述可包含较短气候关键词，但保留国家高亮并拒绝局部交叉重叠。

Desktop/mobile acceptance passed, including a new forest-and-water passage and card navigation. History/Saved browser regression checks also passed with no page errors and zero paid model calls. The expanded 2,000-word local benchmark measured p95 114.23 ms, mean 57.89 ms, and card p95 1.97 ms on this machine. These measurements supersede the smaller-library timing above.

桌面与手机验收通过，增加森林与水文课文及卡片切换检查。历史与收藏浏览器回归也通过，无页面错误或付费模型调用。扩库后的 2,000 词本地基准测得当前设备第 95 百分位 114.23 毫秒、均值 57.89 毫秒，卡片第 95 百分位 1.97 毫秒。这些数值取代上文较小知识库的耗时。

## Library browser acceptance / 知识库浏览验收

All 27 backend tests passed. Library tests enumerate every local ID across pages without duplicates or omissions, check search ranking, category counts, empty results, out-of-range pages, and invalid parameters. Desktop/mobile UI checks passed for opening Library, paging, filtering, searching, selecting a card while preserving the reading, empty results, and Escape dismissal. History/Saved regression checks also passed. No page errors or paid model calls were recorded.

27 项后端测试全部通过。知识库测试逐页遍历全部本地标识，无重复或缺失，并检查搜索排序、分类数量、空结果、超范围分页及非法参数。桌面与手机界面验收覆盖打开 Library、翻页、分类、搜索、保留原文的卡片选择、空结果及 Escape 关闭。历史收藏回归也通过，无页面错误或付费模型调用。

## Material learning and navigation / 材料入库与返回导航

29 backend tests passed. Mocked retrieval verifies automatic promotion, material provenance, offline reuse without duplicate retrieval, restart persistence, failed lookup exclusion, and click-to-retry promotion. Browser desktop/mobile and History/Saved checks passed with no page errors. Browser checks also verify Back to Library preserves the query, Back restores the previous card, and the heading has no italics. These checks make no paid model calls; actual paid extraction was not exercised.

29 项后端测试通过。模拟检索验证自动入库、材料来源、无重复检索的离线复用、重启持久化、失败排除及点击重试入库。桌面、手机及 History/Saved 浏览器检查通过，无页面错误。另验证返回 Library 保留查询、返回上一卡片及标题无斜体。这些检查不产生付费模型调用，未运行真实付费提取。

## Summary acceptance / 摘要验收

31 backend tests passed, covering short/local summaries, the 50-word ceiling, mocked AI output truncation, usage aggregation, cached summaries, safe failure fallback, and long-material sampling. Desktop/mobile browser checks confirm a non-empty bounded summary inside the explorer. History checks restore the same summary without another analysis request. No paid API calls were made during these tests.

31 项后端测试通过，覆盖短文本与本地摘要、50 词上限、模拟 AI 输出截断、用量累计、摘要缓存、安全失败回退及长材料抽样。桌面与手机检查确认摘要位于探索区域内且非空、不超限。历史检查恢复相同摘要，不发起额外分析。这些测试没有调用真实付费 API。


## Full passage and sticky explorer / 全文与吸顶探索区

Desktop/mobile browser acceptance and History/Saved regression checks passed. The additional `scripts/layout_browser_check.py` checks intact long material, no internal passage clipping, aligned panel headings, a visible sticky explorer after scrolling more than 2,000 px, keyword selection without a page jump, explanation scroll reset, collapsible summary, and mobile overflow. Screenshots were reviewed. No paid model calls were made.

桌面与手机浏览器验收及 History/Saved 回归检查通过。新增 `scripts/layout_browser_check.py` 检查长材料完整性、原文没有内部截断、两栏标题对齐、页面滚动超过 2,000 像素后探索区保持可见、点击关键词不发生页面跳转、解释滚动重置、摘要收起及手机横向溢出。已检查截图；没有调用付费模型。

## Guided study acceptance / 引导学习验收

The guided-study browser suite passed on desktop and mobile, covering IndexedDB v1-to-v2 migration with prior-note preservation, confirmed targets, baseline questions, prediction before card exposure, revisions, notebook integration, History restoration, mode switching, hints and supported attempts, interrupted-recall drafts and support labels after reload, immediate/transfer/delayed checks, seven-day review scheduling, simulated due dates, provisional self-assessment, JSON export, storage failures, and linked deletion. Existing browser, personal collections, and long-reading layout checks passed. All 31 backend tests passed using a workspace-local temporary directory. No paid model calls were made. These checks validate functionality, not learning outcomes.

引导学习桌面与手机浏览器套件通过，覆盖 IndexedDB 版本升级与旧笔记保留、目标确认、基线题、解释前预测、修订、笔记整合、历史恢复、模式切换、提示和辅助标记、刷新后的中断回忆草稿及辅助标记、即时迁移及延迟检查、七天复习安排、模拟到期、自评、JSON 导出、存储失败及关联删除。原有浏览器、个人集合及长材料布局检查通过。使用工作区内临时目录运行的 31 项后端测试全部通过。没有调用付费模型。检查验证功能，不证明学习效果。

## Live AI summary recovery / 真实 AI 摘要恢复

On 2026-10-13, the running server's short AI analysis returned local fallback warnings with zero reported tokens. The same summarizer and configured key produced an AI summary in a process with network access. Restarting the verified Atlas server outside the network-restricted sandbox restored the browser upload flow: recognition and a 35-word AI summary completed with no warnings or page errors. This live check made two model calls, reporting 330 input and 196 output tokens; a separate direct diagnostic summary used 111 input and 45 output tokens. Only synthetic geography text was submitted.

2026-10-13，原运行服务的短文本 AI 分析返回本地回退提示，报告 token 用量为零。同一摘要程序及配置密钥在允许联网的进程中生成了 AI 摘要。将经确认的 Atlas 服务重启到网络受限沙箱之外后，浏览器上传流程恢复：识别与 35 词 AI 摘要成功，无警告或页面错误。此次网页检查调用模型两次，报告 330 个输入及 196 个输出 token；独立摘要诊断使用 111 个输入及 45 个输出 token。仅提交了合成的地理测试文本。

All 39 backend tests passed, including new mocked authentication, permission, quota, rate-limit, missing-model, provider-failure, connection, and timeout cases. Tests verify the notices disclose neither credentials nor provider-echoed material. Previously saved History summaries are not automatically regenerated.

39 项后端测试全部通过，包括新增的模拟认证、权限、额度、限流、模型缺失、服务失败、连接及超时情况。测试确保提示不泄露密钥或服务商回显的材料。已经保存到 History 的摘要不会自动重新生成。
# 2026-10-13: Bundled demos and fixed library / 内置案例与固定知识库

41 backend tests passed. New regression tests confirm that AI discovery does not fetch or promote online concepts during analysis, clicking an online card only populates its temporary cache, Library/search/local recognition remain unchanged, and legacy learned rows are excluded without erasing existing data. All ten bundled materials are returned verbatim, retain source/licence headers, and can be analyzed with a summary of at most 50 words. These checks supersede the older automatic-promotion checks recorded below.

41 项后端测试通过。新增回归检查确认：AI 发现新概念时不自动检索或入库，点击在线卡片仅生成临时缓存，Library/搜索/本地识别不增加条目，旧版 learned 数据不再载入且既有数据没有被删除。十份内置材料全文与原文件一致，保留来源和许可声明，可正常分析并生成不超过 50 词的摘要。此处检查取代下方记录的旧版自动入库验收。

Browser acceptance passed for all ten demo choices, preview word counts, normal History submission, desktop/mobile layout, and an online Saved card reopened after refresh with card lookup requests blocked. History/Saved/notes and Guided study regression scripts passed without page errors. The Windows study export check now explicitly reads UTF-8. NativeSelect padding was corrected to avoid clipped option text. The frontend production build passed. No paid model calls were made during these checks.

浏览器验收覆盖十个案例选项、预览词数、正常 History 提交、桌面与手机布局，以及在线词条收藏后刷新、阻断卡片检索仍可打开。History/Saved/笔记与 Guided study 回归脚本均通过，无页面错误。Windows 学习证据导出验收明确按 UTF-8 读取；NativeSelect 调整内边距以避免选项文字裁切。前端生产构建通过。上述检查没有付费模型调用。



## 2026-10-14: Guided targets and one-click unknown answers / 引导目标与一键尚不知道

The frontend build and targeted browser acceptance passed. A deforestation reading automatically selects Deforestation and Forest despite the presence of an unrelated authored Water cycle question pack. Students can replace suggestions and select four targets; all four appear in the baseline and explanation checks. Empty text and unselected confidence do not block I don't know yet: prediction opens the explanation, and assessment advances directly, preserving a low-confidence unknown answer. No paid model calls are made. Broader UX changes remain proposals pending the user's decision.

前端构建与专项浏览器验收通过。森林砍伐材料默认推荐 Deforestation 和 Forest，未被材料中偶然出现、已有专门题组的 Water cycle 优先占据。学生可替换推荐并选择四个目标，四个均进入学前和解释检查。文本为空、尚未选择信心时，I don't know yet 仍可直接打开解释或进入下一题，并保存低信心且尚不知道的回答。不增加付费模型调用。整体体验优化仍为建议，等待用户决定。
## 2026-10-14: Sequential guided navigation / 逐个概念导航

The production frontend build passed. Browser acceptance verifies automatic opening of the first target after baseline, one visible primary action during reading and revision, explicit Read → Revise progression, automatic next-target navigation after saving, and immediate-check entry after the final revision. Free exploration can return to the unfinished target. Desktop and mobile checks passed without page errors; the broader guided-study regression also passed, including notebook integration, restoration, delayed reviews and export. No paid model calls were made. Target ranking remains the existing local heuristic; AI ranking has not been added.

前端生产构建通过。浏览器验收验证学前检查后自动打开首个目标，阅读与修订阶段各有一个可见主按钮，Read → Revise 顺序明确，保存后自动进入下个目标，最终修订后进入即时检查。自由探索可返回未完成目标。桌面和手机验收无页面错误；完整引导学习回归也通过，包括笔记整合、恢复、延迟复习与导出。不产生付费模型调用。目标推荐仍采用本地启发式规则，没有新增 AI 排序。



## 2026-10-14: AI target selection / AI 目标推荐

51 backend tests passed, covering explicit online candidates, invalid count/ID/duplicate/reason rejection, safe connection fallback, no-call disabled mode, cache isolation and combined usage. The frontend build and AI-target browser acceptance passed: exactly two returned targets were selected, reasons were displayed, user changes were permitted, and reopening History or target setup caused no extra analysis calls. A real configured-model call on a fixed demonstration passage selected Deforestation, Soil erosion and Forest with no warning: one call, 608 input and 86 output tokens. This confirms API functionality, not comparative recommendation accuracy. Earlier notes that AI ranking was not implemented are superseded by this entry.

51 项后端测试通过，覆盖明确在线候选、无效数量/标识/重复/理由拒绝、安全连接回退、关闭时零调用、缓存隔离和总用量。前端构建及 AI 推荐浏览器验收通过：仅勾选返回的两个目标、显示理由、允许用户修改，重开 History 或目标设置不增加分析调用。真实配置模型对固定演示材料推荐 Deforestation、Soil erosion 和 Forest，无提示错误：一次调用，608 输入、86 输出 token。这证明接口可用，不代表已验证推荐准确率优于规则。此前关于未实现 AI 排序的记录由本节取代。
## 2026-10-15: Reading-first Guided study / 阅读优先引导学习

51 backend tests passed and the production frontend built successfully. New tests cover mixed quiz generation, at most five questions, source sentence IDs, correct answer indices, invalid output exclusion, safe failures, opt-in generation and cached retries. Browser acceptance covers an empty homepage without analysis calls, default Guided mode, frequency order with no preselection, zero selected concepts, reflection-before-source display, explicit comparison completion, per-question feedback and completion, History restoration without calls, deselection/reselection recovery, Saved access from Guided mode and mobile layout. History/Saved/notes and all ten demo materials passed regression checks. No page errors occurred.

51 项后端测试通过，前端生产构建成功。新增测试覆盖混合小测生成、最多五题、来源句子标识、正确答案索引、无效结果排除、安全失败、按需生成及缓存重试。浏览器验收覆盖无分析调用的空白首页、默认 Guided、频率排序且未预勾选、零目标、先理解后显示解释、明确比对完成、逐题反馈及完成、History 无调用恢复、取消再选择恢复、Guided 内 Saved 访问及手机布局。History/Saved/笔记与十份案例回归通过，无页面错误。

A real configured-model call on the bundled hydrological-cycle material generated five mixed questions without warnings (1,524 input / 380 output tokens). Earlier attempts were rejected because generated quotations were not verbatim; evidence selection was changed to sentence IDs and source reconstruction before successful verification. This verifies the API and source provenance, not validated pedagogical accuracy or mastery assessment. Superseded guided-assessment tests and AI-target code were removed; prior browser study data is archived rather than erased.

真实配置模型基于内置水循环案例成功生成五道混合题，无错误提示（1,524 输入 / 380 输出 token）。此前因模型生成引用非原句而拒绝结果，改为句子标识选择与原文还原后验证成功。这证明接口与引用来源可用，不代表已验证教学准确性或知识掌握。已移除旧版长评估测试和 AI 目标代码，旧浏览器学习数据归档而非删除。

## 2026-10-15: New material entry / 新材料入口

Removed the western-Europe sample file, API endpoint and sample button. The homepage immediately opens New material with empty fields; closing it shows a welcome panel. No analysis or model call occurs on startup. Classic scripts use the frontend build version in their URLs and HTML/JavaScript are revalidated to avoid stale interface code. The production build, 51 backend tests and current guided-flow acceptance passed. The old sample endpoint returns 404.

已移除西欧示例文件、接口及按钮。首页立即打开 New material，输入为空；关闭后显示欢迎页。启动不执行分析或模型调用。经典脚本 URL 包含前端版本，HTML/JavaScript 重新校验缓存，避免旧界面代码。生产构建、51 项后端测试及当前引导流程验收通过，旧示例接口返回 404。



## 2026-10-15: Automatic completion and persistent status / 自动完成与常驻状态

Successful saved understanding submissions now complete concept activities automatically after source retrieval. The extra comparison checkbox and requested explanatory/tagline text were removed. The shared status is a direct child of the sticky explorer, above summary and activity tabs, outside scrolling content; mobile uses sticky status within the explorer. Production build and browser acceptance passed, covering immediate completion, persistence after History restoration, unchanged status position when switching activities or scrolling, and visibility in Explore freely. No paid model calls were made.

理解提交与来源检索成功保存后自动完成概念任务。移除额外比对勾选及指定说明、标语。共用状态栏位于粘性探索区标题下、摘要和活动标签上方，独立于内容滚动；手机端在探索区内吸顶。生产构建与浏览器验收通过，覆盖立即完成、History 恢复、切换及滚动时位置不变、自由探索可见，不调用付费模型。


## 2026-10-15: One explorer scrollbar / 探索区单滚动条

The build and browser acceptance passed for removed summary labels, expanded/collapsed summary, unchanged 50-word limit, visible overflow on summary/card contents and one shared scroll region. A 700px-high desktop viewport verifies actual wheel scrolling and a fixed task-status position. Current guided learning, History restore and mobile acceptance passed. No paid model calls were made.

构建与浏览器验收通过：移除摘要标签、全文展开/收起、保持 50 词限制、摘要/卡片没有内层滚动、统一滚动区域。700px 高桌面窗口验证实际鼠标滚轮滚动与状态栏位置固定。当前引导学习、History 恢复和手机验收通过，不调用付费模型。
