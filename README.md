# Atlas — Geography Learning Agent
# Atlas — 地理学习辅助 Agent

An English-only geography reading companion, with bilingual project documentation. Upload or paste a passage, select highlighted concepts, and explore sourced explanations, relationships, quizzes, and maps.

英语地理阅读辅助应用，项目文档采用英中双语。上传或粘贴课文，点击高亮概念，查看附来源的解释、概念关系、练习和地图。

## Quick start / 快速启动

Use the existing Conda environment named `aai`. No Node.js or frontend build is required.

使用现有的 `aai` Conda 环境。无需 Node.js 或前端构建。

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
- A bundled library of 393 source-backed concepts, countries/territories, and major cities. / 内置 393 条附来源的概念、国家或地区及主要城市记录。
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

Only public encyclopedia cards persist in `.runtime/knowledge.sqlite3`, with seven-day expiry for reuse. Expired records may remain on disk until replaced; this database never stores uploaded passages. Optional external processing remains subject to provider retention policies, even when response storage is disabled.

只有公共百科卡片持久化到 `.runtime/knowledge.sqlite3`，复用有效期为七天。过期记录可能在替换前仍保留于磁盘；该数据库不保存上传课文。即使关闭响应存储，可选外部处理仍受服务商保留政策约束。

This is a local classroom prototype, bound to `127.0.0.1`. Public deployment requires authentication, request limits, HTTPS, and a reviewed retention policy. Do not expose this development server directly to the Internet.

这是绑定 `127.0.0.1` 的本地课堂原型。公开部署需要身份认证、请求限额、HTTPS 和审核后的数据保留政策。不要直接将开发服务暴露到互联网。

## Tests / 测试

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
