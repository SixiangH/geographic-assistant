# Data Sources and Licences
# 数据来源与许可

## Wikipedia / 维基百科

The builder retrieves selected English article introductions through the MediaWiki Action API. Each record retains the canonical article URL, revision ID, source timestamp, and retrieval timestamp. Text is a bounded excerpt, or an explicitly labelled study adaptation accompanied by the excerpt. Revision links allow inspection of the cited version.

构建脚本通过 MediaWiki Action API 获取精选英语条目简介。记录保留正式条目链接、版本标识、来源时间及检索时间。文本是有限摘录，或明确标注并附摘录的学习改写。版本链接可检查引用版本。

Wikipedia text is reused under CC BY-SA 4.0, subject to the article's applicable terms. Attribution is displayed on each card. Modified study-guide text should retain appropriate attribution and share-alike terms when redistributed. Images from Wikipedia are not included.

Wikipedia 文本依据 CC BY-SA 4.0 再利用，并遵守条目适用条款。每张卡片显示署名。重新分发修改后的学习解释时，应保留适当署名与相同方式共享条件。不包含 Wikipedia 图片。

References / 参考：[Wikimedia Terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), [MediaWiki TextExtracts](https://www.mediawiki.org/wiki/Extension:TextExtracts).

## Natural Earth / Natural Earth

World outlines and country attributes come from `ne_110m_admin_0_countries.geojson` in the official Natural Earth vector repository. These data are public domain. Country cards show the source's continent, subregion, and dated population estimate. The SVG displays source geometry and labels any coordinate as a representative point.

世界轮廓和国家属性来自 Natural Earth 官方矢量仓库中的 `ne_110m_admin_0_countries.geojson`，属于公共领域。国家卡片展示来源中的洲、分区及带年份人口估计。SVG 展示来源几何，并将坐标标为代表点。

This is a low-resolution educational world map, not a survey map. Natural Earth's boundary choices and sovereignty classifications may differ from a particular curriculum or jurisdiction. The app does not infer an authoritative political status from the source.

这是低分辨率教学世界地图，不是测绘地图。Natural Earth 的边界及主权分类可能与具体课程或地区不同。应用不依据该来源推断权威政治地位。

References / 参考：[Natural Earth terms](https://www.naturalearthdata.com/about/), [source file](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson).

## GeoNames / GeoNames

The seed contains 70 populous city records selected from `cities15000.zip`. It retains names, coordinates, feature type, time zone, and record modification date. Country names are joined from Natural Earth ISO codes. City population is omitted because the export does not supply an appropriate reference year for that field.

初始数据包含从 `cities15000.zip` 中选择的 70 条人口较多城市记录，保留名称、坐标、实体类型、时区及修改日期。国家名称通过 Natural Earth ISO 代码关联。城市人口因该字段缺乏适当统计年份而不展示。

The current extract readme specifies CC BY 4.0. Cards link to their GeoNames entry and display the licence. Data are supplied without guarantees of accuracy or completeness.

当前导出说明指定 CC BY 4.0。卡片链接到对应 GeoNames 条目并显示许可。数据不保证准确性或完整性。

References / 参考：[GeoNames exports](https://www.geonames.org/export/), [extract readme](https://download.geonames.org/export/dump/readme.txt), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Wikidata and external maps / Wikidata 与外部地图

Online Wikipedia lookup may retrieve a linked Wikidata entity. Population statements require a point-in-time qualifier; deprecated statements and undated values are excluded. The most recent available year is shown, not claimed to be today's population. Wikidata structured data are CC0.

在线 Wikipedia 查询可获取关联 Wikidata 实体。人口陈述必须有时间限定，排除弃用陈述和无日期数值。展示最近可用年份，不称为今日人口。Wikidata 结构化数据采用 CC0。

External OpenStreetMap and Google Earth links are generated from coordinates. The app does not use the public Nominatim geocoder or download public map tiles. External services have their own availability and terms.

根据坐标生成外部 OpenStreetMap 和 Google Earth 链接。应用不使用公共 Nominatim 地理编码服务，也不下载公共地图瓦片。外部服务有独立可用性和条款。

References / 参考：[Wikidata licensing](https://www.wikidata.org/wiki/Wikidata:Licensing), [OpenStreetMap policies](https://operations.osmfoundation.org/policies/), [Google Earth](https://earth.google.com/).
