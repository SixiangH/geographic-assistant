# shadcn/ui Frontend / shadcn/ui 前端

**Date / 日期:** 2026-10-13

## Compatibility and installation / 兼容性与安装

The original FastAPI + vanilla JavaScript project had no React or Tailwind build. shadcn/ui requires a compatible React frontend and Tailwind styling, so it could not be pasted directly into the original HTML. A Vite frontend was added in `frontend/`, following the official [Vite installation](https://ui.shadcn.com/docs/installation/vite) and [component configuration](https://ui.shadcn.com/docs/components-json). The existing Python environment and API remain in use.

原项目使用 FastAPI 与原生 JavaScript，没有 React 或 Tailwind 构建。shadcn/ui 需要兼容的 React 前端与 Tailwind 样式，不能直接粘贴到旧 HTML 中。依据官方文档在 `frontend/` 中加入 Vite 前端，继续使用现有 Python 环境与 API。

The official shadcn CLI installed Button, Card, Input, Textarea, Badge, Label, Separator, and Native Select source components. Installed versions include React/React DOM 19.3.0, Vite 7.3.7, Tailwind 4.3.3, shadcn CLI 4.21.4, and Radix UI 1.8.0. Exact dependency resolutions and integrity hashes are preserved in `frontend/pnpm-lock.yaml`; the CLI is pinned. pnpm permits the required esbuild build script explicitly in `pnpm-workspace.yaml`. Installation does not change global Node or Python settings.

通过官方 shadcn CLI 安装 Button、Card、Input、Textarea、Badge、Label、Separator 与 Native Select 源码组件。安装版本包括 React/React DOM 19.3.0、Vite 7.3.7、Tailwind 4.3.3、shadcn CLI 4.21.4 及 Radix UI 1.8.0。`frontend/pnpm-lock.yaml` 保留依赖的精确解析版本与完整性哈希，CLI 固定版本。`pnpm-workspace.yaml` 明确允许所需的 esbuild 构建脚本。不改变全局 Node 或 Python 设置。

## Rendering contract / 渲染约定

`frontend/src/App.jsx` renders the page shell once with real shadcn components. Inputs are uncontrolled. `main.jsx` commits the shell before loading the four existing classic scripts in sequence, then starts the agent. The React root is intentionally not re-rendered: cards, passage highlights, collection lists, counters, and study forms belong to the existing imperative controllers. Do not add React state that reconciles those controller-owned regions. A future full React migration must move those controllers and their state together, rather than letting both systems write the same DOM.

`frontend/src/App.jsx` 使用实际 shadcn 组件单次渲染页面框架，输入框采用非受控方式。`main.jsx` 在页面提交后按顺序加载四个原有经典脚本，再启动 Agent。React 根节点有意不重复渲染：卡片、高亮、集合列表、数量及学习表单继续由原有命令式控制器管理。不要加入会重新协调这些区域的 React 状态。未来完整迁移 React 时，应一起迁移控制器及状态，避免两个系统同时改写同一 DOM。

The native dialog, checkbox, and tab behavior is retained where the existing agent relies on browser methods or properties. Dialogs receive the new design, focus styling, and Lucide icons. `atlasUI.decorate()` applies the installed shadcn Button variants to dynamically created controls. The CSS theme maps legacy colors to the new design tokens without changing business selectors. No model calls were added by the UI layer. No API keys are bundled into the browser.

原有 Agent 依赖浏览器方法或属性的 dialog、checkbox 和 tab 行为保留。弹窗使用新版样式、焦点提示与 Lucide 图标。`atlasUI.decorate()` 把已安装的 shadcn Button 变体应用到动态控件。CSS 主题把旧颜色映射到新版设计变量，保留业务选择器。UI 层不新增模型调用，不把 API 密钥打包到浏览器。

## Build and run / 构建与运行

Normal use: start the existing FastAPI service with Conda `aai` as before and open `http://127.0.0.1:8000/`. Prebuilt browser assets are included in `app/static/ui/`. The browser origin, database name, and IndexedDB version stay unchanged, so existing History, Saved, and study records are retained.

正常使用：和之前一样使用 Conda `aai` 启动 FastAPI，并打开 `http://127.0.0.1:8000/`。`app/static/ui/` 包含预构建资源。浏览器来源、数据库名称及 IndexedDB 版本保持不变，保留已有 History、Saved 和学习记录。

For frontend development / 前端开发：

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm build
```

From the project root on this workstation, `powershell -ExecutionPolicy Bypass -File scripts/build_frontend.ps1` builds with installed Node or the available bundled Node runtime. Dependencies must already be installed. `pnpm build` compiles to the dedicated `app/static/ui/` directory, then mirrors the generated entry into `app/static/index.html` so an already-running service also receives the update. FastAPI selects the built entry when available. The old interface is retained as `app/static/legacy-index.html` and is the backend fallback if the built entry is missing.

在当前工作站的项目根目录运行 `powershell -ExecutionPolicy Bypass -File scripts/build_frontend.ps1`，可使用已安装 Node 或现有捆绑运行时构建；前提是已安装依赖。`pnpm build` 输出到专用 `app/static/ui/` 目录，再把生成入口同步到 `app/static/index.html`，让已运行服务也获得更新。FastAPI 优先选择构建入口；旧界面保留为 `app/static/legacy-index.html`，作为构建入口缺失时的后端回退。

For hot reload, run FastAPI and `pnpm dev` together, then open the Vite URL ending in `/static/ui/`. The Vite proxy forwards API and controller script requests to port 8000. Vite's port is a different browser origin and therefore has its own browser data; use port 8000 for the existing personal records. Production assets are self-hosted and do not require a CDN, a second running frontend server, or relaxed content security policy.

热更新开发时同时运行 FastAPI 与 `pnpm dev`，打开以 `/static/ui/` 结尾的 Vite 地址。Vite 代理将 API 与控制器脚本请求转发到 8000 端口。Vite 端口是不同的浏览器来源，因此有独立浏览器数据；访问原有个人记录请使用 8000 端口。生产资源由本地服务提供，不需要 CDN、额外前端服务或放宽内容安全策略。

## Verification / 验证

`scripts/shadcn_browser_check.py` verifies actual component slots, native control integration, legacy controller tab state, dynamic button variants, card navigation, mobile text-area height, browser errors, failed requests, and CSP console errors. The existing general browser, History/Saved, guided-study, long-reading sticky-layout, and 31 backend tests also pass. UI regression checks use local analysis and make no paid model calls.

`scripts/shadcn_browser_check.py` 验证实际组件标识、原生控件兼容、原有标签状态、动态按钮变体、卡片导航、手机文本框高度、浏览器错误、失败请求及 CSP 控制台错误。原有通用浏览器、History/Saved、引导学习、长材料吸顶布局检查及 31 项后端测试也通过。UI 回归使用本地分析，不调用付费模型。
## Visual separation / 视觉分区（2026-10-15）

Theme-only refinements distinguish the reading header in deep green, explorer header in deep blue, material summary in pale gold, concept status in green and quiz status in blue. A cooler page background, stronger borders, darker secondary text, selected tabs and highlights make sections easier to identify. Correct and incorrect quiz feedback use distinct green and amber surfaces; disabled answer text remains readable. No markup selectors, application logic, navigation or data behavior changed. Desktop and mobile guided-flow acceptance passed and screenshots were inspected.

仅调整主题样式：阅读标题深绿、探索标题深蓝、材料摘要浅金，概念状态与题目状态分别为绿、蓝。页面底色、边框、次要文字、选中标签和高亮加强分区。正确和错误反馈采用不同绿色与琥珀色背景，已禁用答案仍保持可读。未改变业务选择器、应用逻辑、导航或数据行为。桌面与手机引导流程验收通过，并已检查截图。

## Reading annotations / 阅读标注（2026-10-15）

All geographic annotations now use thin green underlines with transparent backgrounds and normal text color. Hovered or selected terms use a slightly thicker, darker green underline instead of a filled highlight. Dotted/dashed underline styles preserve inferred/ambiguous cues; keyboard focus and clickable behavior remain. Production build and desktop/mobile guided acceptance passed.

地理标注统一为细绿色下划线，背景透明、文字保持正文颜色。悬停或选中时仅加深、加粗绿色下划线，不再填色。点线/虚线保留推断及歧义提示，键盘焦点与点击功能保留。生产构建及桌面/手机引导验收通过。



## Shared explorer scrolling / 探索区统一滚动（2026-10-15）

Summary word-count labels are removed; the 50-word generation limit remains. Every newly opened/restored material starts with the full summary expanded; it can be collapsed, with no independent summary scrollbar. Summary, activity tabs, search, navigation and card/study contents share one desktop scroll region. The title and task status remain outside that region. Selecting an explanation scrolls it into the shared region. Mobile uses normal page scrolling. Keyboard interactions, History and quiz behavior are retained.

移除摘要词数标签，保留生成时 50 词限制。新打开或恢复材料时默认完整展开摘要，可收起，无独立摘要滚动条。桌面摘要、活动标签、搜索、导航及卡片/学习内容共用一个滚动区域；标题和任务状态保留在区域外。选择解释时定位到统一滚动区域内。手机端正常整页滚动。键盘、History 和小测交互保留。
