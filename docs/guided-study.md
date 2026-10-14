# Reading-first Guided Study / 阅读优先引导学习

**Updated / 更新:** 2026-10-15

## Learning flow / 学习流程

The initial page opens New material automatically with empty title and text fields: no sample is analyzed and no model call is made. The former western-Europe sample and its endpoint have been removed. Closing the dialog leaves a welcome panel with a New material button. New material defaults to Guided study. Students may select a bundled reading, paste text or upload a UTF-8 file; Explore freely remains available.

首次打开页面自动显示 New material，标题与文本为空，不分析示例、不调用模型。已移除旧版西欧示例与接口。关闭窗口后仅显示欢迎提示与 New material 按钮。New material 默认选择 Guided study。学生可选择内置案例、粘贴文本或上传 UTF-8 文件，并仍可选择 Explore freely。

After analysis, the concept picker lists distinct, resolved concepts explicitly mentioned in the reading, sorted by total occurrence count (ties follow first appearance). Nothing is preselected. Students choose only unfamiliar concepts; no selection is also allowed. Inferred interpretations and unresolved ambiguities do not enter this picker. Students may change their selection later. Deselecting a concept preserves its earlier understanding and comparison in a browser-side archive so reselecting it restores that work.

分析后按出现总次数排列材料中明确出现、已解决歧义的不同概念；次数相同则按首次出现顺序。初始全部不勾选。学生仅选择不熟悉的概念，也允许不选择。推断解释和未解决的歧义不进入选择器。之后可修改选择；取消概念时，理解和比对记录仍保留在浏览器内，重新选中可恢复。

There is no learning-goal form, baseline assessment, confidence question, mandatory revision or delayed-review sequence. Students read first, then return to selected concepts whenever they want.

不再要求学习目标表单、学前检查、信心问答、强制修订或延迟复习。学生先阅读，再随时返回所选概念。

## Right-side workspace / 右侧学习区

Material summary remains available above three activity tabs:

材料摘要保留在三个活动入口上方：

- **Unfamiliar concepts:** select a chosen concept, write a short understanding or uncertainty, and click Submit and compare. The attributed knowledge-library or online encyclopedia explanation is displayed only after successful submission. A successfully saved submission with a sourced explanation completes the concept activity automatically; no additional comparison checkbox is required.
- **不熟概念：** 随时选择目标，简短填写理解或疑问，点击 Submit and compare。提交成功后显示附来源的知识库或在线百科解释。理解与来源解释成功保存后自动完成概念任务，不需要额外勾选确认。
- **Quick quiz:** up to five material-grounded multiple-choice and true/false questions. Selecting an option reveals correct/incorrect feedback, the correct answer, an explanation and a sentence from the material. The first saved answer is retained and other options disabled for that attempt. Reading remains available; this is formative practice.
- **小测：** 总数不超过五题，包含基于材料的选择题和判断题。选择后显示对错、正确答案、解释及原文句子。保留首次成功保存的回答，并禁用该题其他选项。仍可参照原文，这是形成性练习。
- **Explore:** existing sourced cards, maps, links, relationship navigation and Saved remain available. Clicking an unfamiliar selected highlight returns to its understanding panel; other highlights open normal exploration. Standalone card quizzes are suppressed in Guided mode to avoid extra questions, but retained in Explore freely.
- **探索：** 保留来源卡片、地图、链接、关系导航和 Saved。点击所选不熟概念的高亮返回理解面板，其他词条打开正常探索。Guided 模式不再显示单卡片的额外练习，自由探索仍保留。

The shared task status sits directly below the right-side heading, outside activity scrolling. It stays visible across Concepts, Quick quiz and Explore, including free exploration; on mobile it sticks while the explorer scrolls. Unfamiliar concepts are Completed only when every selected concept has a saved understanding and source explanation. No selection is labelled none selected. Quiz is Completed when every question has a saved answer, regardless of correctness. Completion is activity completion, not a mastery judgement.

任务状态常驻右侧标题下方，独立于活动内容滚动；概念、小测、探索及自由探索均可见，手机端在探索区滚动时吸顶。每个所选概念成功保存理解并显示来源解释后，概念任务才显示 Completed。未选择时明确显示 none selected。所有题目均保存回答后小测显示 Completed，与是否答对无关。状态表示活动完成，不表示知识掌握。

## AI and sources / AI 与来源

AI target recommendation is removed. Optional AI recognition can still locate unfamiliar geographic terms absent from the bundled library. Source lookup remains on click/submission; online cards do not join Library, and Saved retains independent complete snapshots.

移除 AI 目标推荐。可选 AI 识别仍能定位内置库没有的地理关键词。来源在点击或提交时检索；在线卡片不加入 Library，Saved 仍保留独立完整快照。

An AI-enabled Guided submission adds one quiz-generation call. Explore freely does not automatically generate the short quiz. With AI disabled or unavailable, concept learning still works. If the model returns unusable questions, the quiz panel displays a clear notice and offers Generate short quiz when a key is configured. That explicit action sends the material to AI. History reopening reuses generated questions and answers without another call. `/api/study-quiz` also caches successful generation within a session for ten minutes.

启用 AI 的 Guided 提交增加一次出题调用。Explore freely 不自动生成这组小测。关闭 AI 或 AI 不可用时，概念学习仍可用。模型返回无效题目时明确提示，配置密钥后提供 Generate short quiz；点击此按钮明确将材料发送给 AI。重开 History 复用题目与回答，不重复调用。`/api/study-quiz` 在同一会话内缓存成功生成结果十分钟。

The model chooses evidence sentence IDs; the server reconstructs actual source sentences, validates question types, distinct options, answer indices and a total of two to five mixed questions. It does not ask for source-credit trivia. Long inputs use bounded excerpts from throughout the passage. The configured model is unchanged; response storage is disabled. Sentences come from the supplied material, but selecting an evidence sentence does not prove that an AI explanation or answer is semantically correct. A teacher should review the quiz for classroom evaluation. Quiz answer indices are supplied to the browser; it is not a secure exam.

模型选择证据句子的标识，由服务端还原原句，并校验题型、不同选项、答案索引，以及总数为两到五题且包含两种题型。指令要求不考来源声明等细节。长材料使用分布于全文的受限摘录。保持当前模型配置，关闭响应存储。引用来自提交材料，但选中原句不代表 AI 答案与解释在语义上已经验证。课堂评价应由教师审核题目。答案索引发送给浏览器，因此不是安全考试。

## Storage and verification / 存储与验证

New progress uses the existing IndexedDB study store with workflow reading-first. Prior guided-study records are preserved as archived data, and History/Saved/notes are retained. Full answers, comparison checks and quiz responses stay in this browser and are not sent to AI. Clearing site data removes them; there is no device/account sync. Deleting History removes linked current and archived progress.

新进度使用既有 IndexedDB study 存储，标记 reading-first。旧版学习记录保留为归档，History、Saved 和笔记保留。理解、比对勾选和题目回答仅存在当前浏览器，不发送给 AI。清除站点数据会移除记录，没有跨设备或账号同步。删除 History 同时删除关联当前与归档学习记录。

Run `scripts/reading_guide_browser_check.py` for current flow acceptance. It covers the empty homepage, guided default, frequency ordering, no preselection, reflection and source comparison, quiz feedback and completion, History restoration, free exploration and mobile layout. `tests/test_study_quiz.py` covers generation validation, failure notices and cache/usage. Superseded target-recommendation and long guided-assessment browser scripts were removed.

当前流程验收使用 `scripts/reading_guide_browser_check.py`，覆盖空白首页、默认 Guided、频率排序、不预勾选、理解与来源比对、小测反馈及完成、History 恢复、自由探索和手机布局。`tests/test_study_quiz.py` 校验题目生成、失败提示、缓存及用量。已移除被替代的目标推荐与长链路评估浏览器脚本。
## AI-only summary display / 仅启用 AI 时展示摘要

When AI is disabled on submission, the server does not generate a local summary and the summary panel displays “Enable AI when submitting your material to get a summary.” Older non-AI History entries also show this notice instead of their previous extractive summaries. AI-enabled submissions retain the 50-word limit and existing failure notice/fallback behavior. Changing the upload checkbox alone does not regenerate an existing reading; submit the material again with AI enabled.

提交时关闭 AI，服务端不生成本地摘要，摘要区域显示启用 AI 提示。旧版非 AI History 同样显示提示，不展示原有提取式摘要。启用 AI 的提交保留 50 词限制及已有失败提示/回退行为。仅切换上传窗口的勾选不会重新生成既有材料，需要启用 AI 后重新提交。
