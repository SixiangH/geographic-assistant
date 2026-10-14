# Offline Knowledge Coverage
# 离线知识覆盖范围

The library combines selected English Wikipedia article introductions, Natural Earth countries and territories, and GeoNames cities. It is a curated classroom collection rather than a complete encyclopedia. Definitions are source excerpts; their revision, retrieval date, canonical link, and licence are retained on each card. English materials and the student interface remain English-only.

知识库结合精选英语 Wikipedia 条目简介、Natural Earth 国家与地区及 GeoNames 城市数据。这是教学精选集合，并非完整百科。解释使用来源摘录，每张卡片保留版本、检索时间、正式链接与许可。学生界面及上传材料继续只使用英语。

## Extended classroom topics / 扩展教学主题

| Area / 领域 | Examples / 示例 |
|---|---|
| Ecosystems and vegetation / 生态系统与植被 | Forest, woodland, lake, wetland, grassland, mangrove, habitat, biodiversity / 森林、林地、湖泊、湿地、草原、红树林、栖息地、生物多样性 |
| Environmental change / 环境变化 | Deforestation, reforestation, soil erosion, desertification, eutrophication, coral bleaching / 森林砍伐、再造林、土壤侵蚀、荒漠化、富营养化、珊瑚白化 |
| Water and landforms / 水文与地形 | Groundwater, aquifer, tributary, flood, drought, canyon, cave, beach, moraine / 地下水、含水层、支流、洪水、干旱、峡谷、洞穴、海滩、冰碛 |
| Weather and climate / 天气与气候 | Cloud, fog, rainfall, cold front, tornado, heat wave, urban heat island / 云、雾、降雨、冷锋、龙卷风、热浪、城市热岛 |
| Human geography / 人文地理 | Settlement, urban sprawl, land use, population growth, agriculture, renewable energy / 聚落、城市蔓延、土地利用、人口增长、农业、可再生能源 |
| Geography skills / 地理技能 | Topography, elevation, topographic map, cartography, geomorphology / 地形、海拔、地形图、制图学、地貌学 |

The editable catalog is `data/additional-topics.txt`: `Wikipedia title|category|semicolon-separated aliases`. Aliases include selected plural forms and British/American spelling variants. Missing articles, disambiguation pages, empty excerpts, and records without a revision are skipped and reported, rather than supplied with invented explanations. Broad everyday terms can still match in non-geographical contexts; the local recognizer is a vocabulary matcher, not a complete semantic classifier.

可编辑目录为 `data/additional-topics.txt`，格式为 `Wikipedia 标题|类别|以分号分隔的别名`。别名包含精选复数及英美拼写。缺失条目、消歧义页面、空摘录及缺少版本的记录会跳过并报告，不编造解释。部分日常词也可能在非地理语境中匹配；本地识别是词汇匹配，并非完整语义分类器。

Relationships labelled “mentioned in source” connect concepts literally named in the excerpt. These links help exploration and do not assert a causal relationship. Existing curated relationships and quizzes are retained.

标为 “mentioned in source” 的关系连接摘录实际提到的概念，用于探索，不表示因果关系。已有人工精选关系及练习保留。

Some specialized terms redirect to a broader Wikipedia article. Their cards cite that actual article, and the introductory excerpt may describe the wider topic rather than the specific subsection. These records are source excerpts, not independently reviewed textbook explanations.

部分细分术语会重定向到更广泛的 Wikipedia 条目。卡片引用实际来源条目，简介可能描述较大的主题，而非具体小节。这些记录是来源摘录，不是经过独立审核的课本解释。

## Extending and rebuilding / 扩充与重建

```powershell
conda activate aai
python scripts/expand_knowledge.py
```

This command adds missing catalog entries to the existing library without refreshing countries, cities, or existing cards. Download batches are cached under ignored `.runtime/topic-snapshots/` to support retries. It respects source rate limits and replaces the library only after every network batch succeeds. No model is called. Restart the server after a successful build; then refresh the webpage to update its library count.

此命令将目录中尚未收录的条目加入现有库，不刷新国家、城市或已有卡片。下载批次缓存于被 Git 忽略的 `.runtime/topic-snapshots/`，便于重试。脚本遵守来源限流，全部网络批次成功后才替换知识库，不调用模型。成功构建后重启服务，再刷新网页更新条目数量。

`python scripts/build_knowledge.py` rebuilds the original countries, cities, and concepts and then includes this extended catalog. To obtain fresh extended source snapshots during a full rebuild, first remove the local topic snapshot cache. Browser History and Saved retain their original card snapshots; new readings use the expanded library.

`python scripts/build_knowledge.py` 重建原有国家、城市及概念，然后加入扩展目录。完整重建时若需重新获取扩展来源快照，先移除本地条目快照缓存。浏览器 History 和 Saved 保留原始卡片快照；新阅读使用扩展后的知识库。

## Current snapshot / 当前快照

The 2026-10-08 library contains 711 records: 468 Wikipedia concepts and places, 173 Natural Earth countries/territories, and 70 GeoNames cities. All 318 catalog topics were retrieved successfully.

2026-10-08 知识库共 711 条：468 条 Wikipedia 概念与地点、173 条 Natural Earth 国家与地区、70 条 GeoNames 城市。目录中的 318 个主题均已成功获取。

## Bundled library and online snapshots / 内置知识库与在线快照

The local library contains bundled knowledge only. Analysis no longer retrieves or permanently promotes newly discovered concepts; online cards are retrieved on click and cached for seven days outside Library/search. Legacy learned rows are excluded without deleting existing data. Saved stores a complete card and source snapshot in browser IndexedDB, including online concepts absent from the library, so reopening Saved needs neither the server cache nor a new lookup. Material titles and IDs are no longer attached to online cards.

本地知识库仅包含项目内置条目。分析不再自动检索或永久收录新概念；在线卡片在点击时检索，临时缓存七天，不进入 Library/搜索。旧版 learned 数据不再载入知识库，但不删除既有数据。Saved 在浏览器 IndexedDB 中保存完整卡片与来源快照，包括知识库中没有的在线条目，因此重开收藏不依赖服务端缓存或重新检索。在线卡片不再附加材料标题与标识。

Explorer navigation retains up to 40 previous card snapshots without repeating source/model calls. Return controls reopen the originating collection with the Library query/category/page preserved. The headline uses one upright serif typeface.

探索导航保留最多 40 张之前的卡片快照，返回不重复来源或模型调用。返回按钮重新打开原集合，Library 保留搜索、分类和分页状态。顶部标题统一采用正体衬线字体。
