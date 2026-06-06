# 系统架构

## 目标

在指定运行日回看最近 6 个月，持续发现、采集、抽取和分析公开互联网中与保险相关的用户评论。系统需要能解释每条数据从哪里来、为什么被保留、如何被分类，以及是否经过脱敏。

## 组件

```text
seed taxonomy
  -> real_time_signal_probe
  -> candidate signals
  -> compliance gate
  -> source planner
  -> frontier queue
  -> collectors
  -> parsers
  -> extraction agent
  -> normalization and dedupe
  -> analysis agent
  -> quality audit
  -> warehouse
  -> reports and alerts
```

## Agent 职责

| Agent | 输入 | 输出 | 关键约束 |
| --- | --- | --- | --- |
| Real-time Signal Probe | 保险主题、竞品、时间窗口、平台配置 | 30 天候选信号、趋势摘要、竞品对比、引用来源、互动权重 | 只做发现和优先级排序，不直接写入评论主库 |
| Source Planner | 保险词库、品牌词、历史高价值来源 | 查询词、来源候选、优先级 | 必须带时间窗口和来源类型 |
| Compliance Gate | URL、平台规则、robots、来源类型 | allow/deny/review | 不绕过登录，不抓私域内容 |
| Collector | 采集任务、适配器配置 | 原始页面、评论 API 响应、截图证据 | 限速、重试、状态持久化 |
| Extraction | 页面文本/HTML、截图、schema | 候选评论记录 | 必须返回结构化字段 |
| Normalizer | 候选记录 | 标准记录、重复关系 | 时间、URL、文本哈希一致 |
| Analyzer | 标准记录、标签体系 | 情感、方面、意图、风险标签 | 低置信度进入人工抽样 |
| QA Auditor | 样本记录和原始证据 | 质量问题、修复建议 | 记录可复现 |

## 数据流

1. Real-time Signal Probe 使用 `last30days-skill` 和 `last30days-skill-cn` 对保险主题、竞品、渠道和产品做近 30 天脉冲搜索，输出候选信号、趋势摘要、竞品对比、引用来源和互动权重。
2. Compliance Gate 检查候选信号来源是否公开、是否允许采集、是否需要降频或人工审批。
3. Source Planner 将通过合规门的高价值候选信号转化为近半年采集计划，例如“保险 理赔 拒赔”“重疾险 退保”“医疗险 续保”“保险代理人 误导销售”。
4. Frontier Queue 按来源、关键词、时间窗口保存任务，支持断点续跑和重复 URL 跳过。
5. Collector 根据来源选择 API、HTTP crawler 或 browser automation。
6. Parser 清洗导航、广告、推荐区等噪声，保留评论上下文和页面证据。
7. Extraction Agent 输出 `InsuranceMention` schema。
8. Normalizer 过滤 2025-12-05 至 2026-06-05 之外的历史评论，并生成内容哈希。
9. Analyzer 做情感、方面和意图识别。
10. QA Auditor 抽样检查原文、链接、发布时间和脱敏结果。
11. Warehouse 保存结构化记录，Report 层按公司、产品、渠道、情感、问题类型聚合。

## 30 天脉冲层

`last30days` 的定位是实时发现层，不是完整爬虫替代品。其输出进入 `candidate signals`，只有在完成来源可追溯、时间过滤、去重、PII 检查和人工抽样后，才可被提升到近半年主库。

推荐数据流：

```text
last30days pulse
  -> candidate signals
  -> compliance gate
  -> source planner
  -> collectors / warehouse
```

预留对象：

- `RealTimeSignalProbe`：一次 30 天实时研究任务，记录查询词、平台范围、运行时间和输出路径。
- `RealTimeSignal`：单个平台或来源返回的候选信号，包含 topic、platform、source_url、published_at、observed_at、engagement_metrics、summary、citations。
- `ComparativePulseReport`：竞品对比输出，包含 competitors、strengths、weaknesses、source_counts、engagement_weighted_findings。
- `SignalPromotionPolicy`：定义实时信号进入近半年主库前必须通过的验证、脱敏和审计规则。

## 存储建议

- Raw zone：原始响应、截图、HTML，仅短期保存并加密，默认不进 Git。
- Clean zone：脱敏后的评论文本、来源、时间、标签。
- Feature zone：实体、情感、方面、embedding、聚类结果。
- Audit zone：采集日志、robots/ToS 检查、模型版本、人工复核结论。

## 技术选型建议

- 采集队列：Apify Request Queue、Redis Queue、Postgres job table 或 Temporal。
- 爬虫：Crawlee、Playwright、Scrapy，按来源复杂度选择。
- Agent 编排：LangChain、Pydantic AI、Agno 或轻量自研 planner。
- 结构校验：Pydantic / JSON Schema。
- 实时情报脉冲：`last30days-skill` 用于全球平台，`last30days-skill-cn` 用于中文平台，输出候选信号与引用。
- 结构化抽取：LangExtract 或同类 source-grounded extractor，保存字段与原文 span。
- 主题建模：BERTopic 起步，按周/月使用 topics-over-time 追踪近半年主题迁移。
- 分析存储：DuckDB 起步，Postgres + pgvector 或 ClickHouse 进入规模化。
- 报告：Notebook、Metabase、Superset 或静态 Markdown 报告。

## 可选扩展

- `research_reporter`：使用 GPT Researcher 风格的检索增强研究报告生成周报/月报。
- `topic_deep_dive`：当 BERTopic 发现异常主题时，用 STORM 风格多视角提问做专题深挖。
- `real_time_signal_probe`：使用 `last30days` 发现最近 30 天高互动热点、竞品对比和新兴平台信号。
- `survey_trigger`：用 Formbricks 对自有用户或许可样本发起定向问卷，验证公开舆情假设。
- `product_analytics`：如果后续建设内部仪表板或标注平台，再接入 PostHog/OpenReplay 监测产品体验。
- `voice_ingestion`：仅在拥有合法授权的访谈或客服音频场景中接入 ASR，例如 VibeVoice。
