# Atlas — Geography Learning Agent
# Atlas — 地理学习辅助 Agent

An English-only geography reading companion, with bilingual project documentation. Upload or paste a passage, select highlighted concepts, and explore sourced explanations, relationships, quizzes, and maps.

英语地理阅读辅助应用，项目文档采用英中双语。上传或粘贴课文，点击高亮概念，查看附来源的解释、概念关系、练习和地图。

## Quick start / 快速启动

Use the existing Conda environment named `aai`. The built shadcn/ui frontend is included, so normal startup does not require Node.js. Editing the frontend requires Node.js 22.12+ and pnpm; see [frontend development](docs/frontend-ui.md).

使用现有的 `aai` Conda 环境。已包含构建好的 shadcn/ui 前端，正常启动不需要 Node.js。编辑前端需要 Node.js 22.12+ 与 pnpm，详见[前端开发说明](docs/frontend-ui.md)。

```powershell
conda activate aai
cd "D:\projects\geographic assistant"
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Stop the server with `Ctrl+C`.

打开 [http://127.0.0.1:8000](http://127.0.0.1:8000)。使用 `Ctrl+C` 停止服务。

On this Windows machine, the startup script also locates the environment under `%USERPROFILE%\miniconda3\envs\aai` and falls back to `conda run` when available.

在本 Windows 设备上，启动脚本也会查找 `%USERPROFILE%\miniconda3\envs\aai`，并在可用时回退到 `conda run`。

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

The bypass applies only to that PowerShell process, not to the machine's permanent execution policy. A different port can be selected with `-Port 8001`.

该执行策略仅作用于本次 PowerShell 进程，不修改设备的永久策略。可通过 `-Port 8001` 指定其他端口。

## What is implemented / 已实现内容

- English text pasting and strict UTF-8 `.txt` upload, limited to 1 MB and 10,000 words. / 英语文本粘贴及严格 UTF-8 `.txt` 上传，上限 1 MB、10,000 个单词。
- Original text and paragraph preservation, including Unicode-safe highlight offsets. / 保留原文和段落，高亮位置兼容 Unicode。
- A bundled library of 711 source-backed concepts, countries/territories, and major cities. / 内置 711 条附来源的概念、国家或地区及主要城市记录。
- Longest-phrase matching, aliases, category filters, and explicit choices for ambiguous names. / 最长短语匹配、别名、类别筛选及歧义名称候选选择。
- Explanation cards with source snapshots, revision links, and population reference years. / 解释卡片包含来源快照、版本链接及人口统计年份。
- Offline world outlines from Natural Earth, country highlighting, zoom controls, and external OpenStreetMap/Google Earth links. / 使用 Natural Earth 的离线世界轮廓，支持国家高亮、缩放及外部 OpenStreetMap/Google Earth 链接。
- Selected source-linked relationships and six recall questions. / 部分附来源的概念关系及六道回忆题。
- Optional bounded AI recognition and approved Wikipedia/Wikidata lookup. / 可选受限 AI 识别及指定 Wikipedia/Wikidata 检索。
- Public-card caching in SQLite and per-session usage reporting. / SQLite 公共卡片缓存及会话用量统计。
- Responsive layout, keyboard controls, source failure handling, and no upload storage on the server's disk. / 响应式布局、键盘操作、来源失败处理及不在服务端磁盘保存上传材料。
- History with stored passages, analysis, ambiguity choices, and viewed source snapshots; reopening does not repeat model analysis. / 历史记录保存课文、分析、歧义选择及已查看来源快照，重新打开不重复模型分析。
- Starred explanations in Saved, with source references, searchable personal notes, and individual or collection deletion. / 收藏星标解释及来源，支持可搜索个人笔记、单条删除及清空集合。

The default sample is ready to explore without a key. Local recognition and the bundled world map do not require external services.

默认示例无需密钥即可使用。本地识别和内置世界地图不依赖外部服务。

## Optional AI configuration / 可选 AI 配置

Copy `.env.example` to `.env`, set an OpenAI API key, and restart the server. Keep the key on the server; never paste it into uploaded materials or commit it to source control.

复制 `.env.example` 为 `.env`，设置 OpenAI API 密钥，并重启服务。密钥仅保存在服务端；不要写入上传材料或提交到版本库。

```dotenv
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
ONLINE_LOOKUP_ENABLED=true
INPUT_PRICE_PER_MILLION=
OUTPUT_PRICE_PER_MILLION=
```

AI is opt-in per analysis. The app sends study text to the OpenAI Responses API with structured output and `store=false`. It requests exact quoted spans, validates them against the original, and does not let the model execute arbitrary tools. AI suggestions are labelled as inferred when appropriate. Missing knowledge is fetched only when selected, and explanation text comes from actual source excerpts.

每次分析可选择是否启用 AI。应用通过 OpenAI Responses API 发送学习文本，使用结构化输出及 `store=false`。要求模型返回原文片段，并与原文校验；模型不能执行任意工具。适用时将建议标为推断。缺失知识只在点击时检索，解释文本来自实际来源摘录。

At most four model calls cover the first 48,000 characters; local matching covers the entire accepted passage. API refusals, incomplete responses, and network errors fall back to local recognition. Actual model access depends on the configured account and model.

最多四次模型调用覆盖前 48,000 个字符；本地匹配覆盖整篇已接受材料。API 拒绝、不完整响应和网络错误会回退到本地识别。实际模型访问取决于配置账号和模型权限。

Price fields are optional USD prices per million tokens. If unset, the app reports cost as unavailable rather than inventing an estimate. They should be updated from your provider's current pricing. Paid AI integration has been tested with mocks; a real key was not available during development.

价格字段为可选的每百万 token 美元价格。未设置时显示费用未知，不编造估算。应根据服务商当前价格更新。付费 AI 集成已使用模拟测试；开发时没有可用真实密钥。

## Data and privacy / 数据与隐私

Successful pasted or uploaded readings are saved in this browser's IndexedDB as History, with their analysis and viewed source snapshots. Starred cards and personal notes are stored in Saved. They survive refresh and server restart, without account sync. Delete individual entries or clear either collection to remove them; clearing browser site data also removes them. Sample lessons and failed analyses are not added to History. Earlier readings from before this feature was installed cannot be recovered automatically.

成功分析的粘贴或上传材料保存到此浏览器 IndexedDB 的 History，包含分析和已查看来源快照。星标卡片与个人笔记保存在 Saved。刷新或重启服务后仍保留，但没有账号同步。可单条删除或清空集合；清除浏览器站点数据也会移除它们。示例和失败分析不加入历史。安装本功能之前的阅读不能自动恢复。

The server never writes uploaded passages to disk. It holds up to 32 session-scoped recognition results for reuse, expiring after 10 minutes with periodic cleanup. Browser storage is limited by the browser's quota: failed writes are reported, and existing entries are not silently evicted.

服务端不将上传课文写入磁盘，最多缓存 32 条会话识别结果，10 分钟后过期并定期清理。浏览器存储受配额限制；写入失败会提示，不会静默淘汰已有条目。

Public encyclopedia lookup cards are temporarily cached for seven days in `.runtime/knowledge.sqlite3`; they are not added to Library or local recognition. The library uses bundled knowledge only. Legacy learned rows are no longer loaded, without deleting existing data. Saved keeps complete explanation and source snapshots in browser IndexedDB, including online cards absent from the library. Full uploaded passages are never stored in this database. Optional external processing remains subject to provider retention policies, even when response storage is disabled.

公共百科检索卡片在 `.runtime/knowledge.sqlite3` 中临时缓存七天，不加入 Library 或本地识别。知识库仅使用内置条目；旧版 learned 数据不再载入，但不删除既有数据。Saved 在浏览器 IndexedDB 保存完整解释与来源快照，包括知识库中没有的在线卡片。该数据库不保存完整上传课文。即使关闭响应存储，可选外部处理仍受服务商保留政策约束。

This is a local classroom prototype, bound to `127.0.0.1`. Public deployment requires authentication, request limits, HTTPS, and a reviewed retention policy. Do not expose this development server directly to the Internet.

这是绑定 `127.0.0.1` 的本地课堂原型。公开部署需要身份认证、请求限额、HTTPS 和审核后的数据保留政策。不要直接将开发服务暴露到互联网。

## Tests / 测试

The upload dialog includes ten bundled English textbook readings: choose **New material → Try a demo material → Use this material**, then review the text and click **Explore this reading**. These readings use the normal History, Saved and Guided study workflow. Source credits and licences remain in the full text. See [Demo Readings](docs/demo-materials.md).

上传窗口内置十份英文教材案例：选择 **New material → Try a demo material → Use this material**，查看文本后点击 **Explore this reading**。案例使用正常的 History、Saved 和 Guided study 流程，完整文本保留来源与许可。详见 [内置试用材料](docs/demo-materials.md)。

Run the backend tests inside `aai`:

在 `aai` 中运行后端测试：

```powershell
python -m pytest -q
```

For browser acceptance checks, install the optional test dependency and keep the server running. The script uses installed Chrome when found; otherwise install Playwright Chromium.

浏览器验收需安装可选测试依赖并保持服务运行。脚本优先使用已安装 Chrome，否则安装 Playwright Chromium。

```powershell
python -m pip install -r requirements-dev.txt
# If Chrome is unavailable / 若 Chrome 不可用:
python -m playwright install chromium
python scripts/browser_check.py
python scripts/personal_browser_check.py
```

Screenshots are written to `test-results/`, which is excluded from version control. See [verification report](docs/verification.md) for scope and limitations.

截图保存于 `test-results/`，该目录不纳入版本控制。测试范围及局限见[验证报告](docs/verification.md)。

## Refresh the public knowledge snapshots / 更新公共知识快照

The application includes data and does not need this step to start. To refresh source snapshots, run the builder and restart the server. It downloads selected Wikipedia introductions, Natural Earth country geometry/attributes, and a GeoNames city extract. It makes no model calls.

应用已内置数据，启动不需要此步骤。更新来源快照时运行构建脚本并重启服务。脚本下载精选 Wikipedia 简介、Natural Earth 国家几何与属性，以及 GeoNames 城市数据，不调用模型。

```powershell
python scripts/build_knowledge.py
```

The city selection uses population only to choose the 70 largest available records. City population is not displayed because the extract lacks a suitable observation year. Country population comes from dated Natural Earth estimates; it is not labelled as current population.

城市筛选仅用人口选择可用记录中的前 70 条。由于导出数据缺乏适当统计年份，界面不展示城市人口。国家人口采用有年份的 Natural Earth 估计值，不称为当前人口。

## Project documents / 项目文档

- [Requirements analysis / 需求分析](docs/requirements-analysis.md)
- [Architecture and API / 架构与 API](docs/architecture.md)
- [Sources and licences / 来源与许可](docs/data-sources.md)
- [Verification and limitations / 验证与局限](docs/verification.md)

PDF/DOCX import, OCR, a full graph editor, fully offline AI, and a teacher dashboard remain outside this version. See the requirements for planned later work.

本版本不包含 PDF/DOCX 导入、OCR、完整图谱编辑器、完全离线 AI 和教师面板。后续计划见需求分析。

See [offline knowledge coverage](docs/knowledge-coverage.md) for the expanded 318-topic catalog and incremental build command.

扩展的 318 个教学主题及增量构建命令见[离线知识覆盖说明](docs/knowledge-coverage.md)。

The header Library opens all local entries with text search, category filters, and pagination. Selecting an entry opens its existing explanation card without changing the reading.

主页 Library 入口展示全部本地条目，支持文本搜索、分类筛选与分页。点击条目打开已有解释卡片，不改变当前阅读材料。

New materials with AI enabled automatically retrieve missing concepts from Wikipedia/Wikidata and add successful sourced cards to Library. Source failures are reported and remain retryable. Without AI, the application recognizes existing local vocabulary. The explorer offers Back, Back to Library/Saved/History, and Back to reading controls.

启用 AI 的新材料会自动从 Wikipedia/Wikidata 检索缺失概念，成功的附来源卡片加入 Library。来源失败会提示并可重试。不启用 AI 时，应用识别现有本地词汇。探索区域提供上一条目、返回 Library/Saved/History 及返回阅读区操作。

## Material summaries / 材料摘要

Every accepted reading receives an English summary of at most 50 whitespace-separated words, shown inside Explore a little deeper, below its heading. Local mode ranks and extracts up to four key sentences without model calls. Enabling AI requests one additional Responses API call for a coherent summary; failed or incomplete responses fall back to local key sentences, with a visible notice. Word limits are enforced on the server even if a model exceeds them. Long AI inputs use bounded representative excerpts across the passage and are labelled accordingly.

每篇已接受材料都生成不超过 50 个按空白分隔英语单词的摘要，展示于 Explore a little deeper 内的标题下方。本地模式排序并提取最多四个关键句，不调用模型。启用 AI 会增加一次 Responses API 调用以生成连贯梗概；失败或不完整响应回退到本地关键句，并显示提示。即使模型超出要求，服务端也会强制限制词数。较长 AI 输入使用遍布原文的受限代表摘录，并明确标注。

Summary text, type, word count, and warnings are stored inside the analysis snapshot in browser History. Reopening a new history record restores the exact summary without model calls. Older history records without summaries show an unavailable notice and may be re-analyzed. Summaries do not change when browsing other knowledge cards, and original material remains unchanged. AI summary usage is included in session token/call/cost accounting. Sample lessons use local summaries only.

摘要文字、类型、词数和提示随分析快照存入浏览器 History。重新打开新历史记录恢复原摘要，不调用模型。没有摘要的旧记录显示缺失提示，可重新分析。浏览其他知识卡片不改变材料摘要，原文保持完整。AI 摘要用量计入会话 token、调用及费用统计。示例课文仅使用本地摘要。


AI assistance is selected by default when an API key is configured. Students can uncheck it for local analysis; refreshing service status preserves that choice while AI remains available. Without a configured API key the option is unchecked and disabled.

配置 API key 后，AI 辅助默认勾选。学生可取消勾选以使用本地分析；AI 持续可用时，刷新服务状态保留此选择。未配置 API key 时，该选项取消勾选并禁用。


## Guided study / 引导学习

Guided study adds confirmed targets, prediction and revision, baseline and recall/transfer checks, seven-day review reminders, browser-only learning evidence, provisional self-assessment, and JSON export. Explore freely remains available. See [Guided Study and Learning Evidence](docs/guided-study.md).

引导学习新增目标确认、预测与修订、基线和回忆或迁移检查、七天复习提醒、仅保存在浏览器的学习证据、暂定自评及 JSON 导出。保留自由探索模式，详见上方双语设计文档。

## AI connectivity troubleshooting / AI 连接排查

An API key being present or passing a model-information request does not prove that the running server can generate summaries. The server process itself needs network access to OpenAI. Starting it in a network-restricted execution sandbox causes recognition and summarization to fall back to local results. Start from an ordinary terminal with network access using `powershell -ExecutionPolicy Bypass -File scripts/start_app.ps1`, or use the existing uvicorn command in Conda `aai`. Restart after changing `.env`. Stop the existing instance before starting another instance on port 8000.

存在 API key 或模型信息查询成功，不能证明当前服务能生成摘要。服务进程本身需要能够连接 OpenAI。在网络受限的执行沙箱中启动服务，会使识别与摘要回退到本地结果。请在允许联网的普通终端运行 `powershell -ExecutionPolicy Bypass -File scripts/start_app.ps1`，或在 Conda `aai` 环境使用原有 uvicorn 命令。修改 `.env` 后重启；启动新实例前先停止占用 8000 端口的旧实例。

Fallback notices distinguish connection failures, timeouts, rejected credentials, missing permissions/model access, quota exhaustion, rate limits, and invalid or incomplete responses. Raw provider messages, keys, and material content are never included in these notices. Local summaries remain available. A History snapshot retains the summary it originally saved; resubmit its material to generate a new AI summary after connectivity is restored. See [official OpenAI error documentation](https://developers.openai.com/api/docs/guides/error-codes).

回退提示区分连接失败、超时、密钥拒绝、权限或模型访问问题、额度不足、限流及无效或不完整响应。提示不包含原始服务商错误、密钥或材料内容。本地摘要仍可用。History 快照保留最初保存的摘要；连接恢复后，需要重新提交材料才能生成新的 AI 摘要。参考上方 OpenAI 官方错误文档。
# Current Guided study / 当前引导学习（2026-10-15）

The page starts without a default passage. New material defaults to Guided study: choose unfamiliar concepts from a frequency-sorted list with no preselection, read, write your understanding when ready, then compare with a sourced explanation. Successful understanding submissions update concept completion automatically; task status stays visible above all right-side activities. A separate Quick quiz tab contains no more than five AI-generated multiple-choice/true-false questions with immediate feedback and activity completion. AI target ranking, baseline/confidence forms and the former extended assessment sequence have been removed. History, Saved and free exploration remain. See [Reading-first Guided Study](docs/guided-study.md); earlier feature descriptions below reflect historical versions.

首页不展示默认课文。New material 默认 Guided study：从按频率排列且未预勾选的列表选择不熟悉概念，阅读后随时写理解，并与有来源的解释比对。成功提交理解后自动更新概念完成状态，任务状态常驻所有右侧活动上方。独立 Quick quiz 提供总数不超过五题的 AI 选择/判断小测，即时反馈并记录任务完成。已移除 AI 目标排序、学前/信心表单及旧版长评估流程。History、Saved 和自由探索保留。详见 [阅读优先引导学习](docs/guided-study.md)；下方早期功能描述反映历史版本。
