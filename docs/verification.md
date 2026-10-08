# Verification Report
# 验证报告

**Date / 日期:** 2026-10-08  
**Environment / 环境:** Windows, Conda `aai`, Python 3.11.16  
**Version / 版本:** 0.1.0

## Completed checks / 已完成检查

All 24 automated backend tests passed. They cover sample recognition, original-text offsets including emoji, longest-phrase matching, ambiguity, non-English and oversized inputs, unsupported control characters, AI configuration and failure fallback, session cache separation, source/cache failures, quiz grading, dated population, maps, and seed integrity.

24 项后端自动测试全部通过，覆盖示例识别、含表情字符的原文位置、最长短语匹配、歧义、非英语与超限输入、不支持的控制字符、AI 配置与失败回退、会话缓存隔离、来源与缓存失败、练习评分、带年份人口、地图及初始数据完整性。

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
