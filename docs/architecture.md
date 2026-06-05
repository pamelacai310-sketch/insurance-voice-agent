# 系统架构

## 目标

在指定运行日回看最近 6 个月，持续发现、采集、抽取和分析公开互联网中与保险相关的用户评论。系统需要能解释每条数据从哪里来、为什么被保留、如何被分类，以及是否经过脱敏。

## 组件

```text
seed taxonomy
  -> source planner
  -> compliance gate
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
| Source Planner | 保险词库、品牌词、历史高价值来源 | 查询词、来源候选、优先级 | 必须带时间窗口和来源类型 |
| Compliance Gate | URL、平台规则、robots、来源类型 | allow/deny/review | 不绕过登录，不抓私域内容 |
| Collector | 采集任务、适配器配置 | 原始页面、评论 API 响应、截图证据 | 限速、重试、状态持久化 |
| Extraction | 页面文本/HTML、截图、schema | 候选评论记录 | 必须返回结构化字段 |
| Normalizer | 候选记录 | 标准记录、重复关系 | 时间、URL、文本哈希一致 |
| Analyzer | 标准记录、标签体系 | 情感、方面、意图、风险标签 | 低置信度进入人工抽样 |
| QA Auditor | 样本记录和原始证据 | 质量问题、修复建议 | 记录可复现 |

## 数据流

1. Source Planner 使用保险主题词生成搜索任务，例如“保险 理赔 拒赔”“重疾险 退保”“医疗险 续保”“保险代理人 误导销售”。
2. Compliance Gate 检查来源是否公开、是否允许采集、是否需要降频或人工审批。
3. Frontier Queue 按来源、关键词、时间窗口保存任务，支持断点续跑和重复 URL 跳过。
4. Collector 根据来源选择 API、HTTP crawler 或 browser automation。
5. Parser 清洗导航、广告、推荐区等噪声，保留评论上下文和页面证据。
6. Extraction Agent 输出 `InsuranceMention` schema。
7. Normalizer 过滤 2025-12-05 至 2026-06-05 之外的历史评论，并生成内容哈希。
8. Analyzer 做情感、方面和意图识别。
9. QA Auditor 抽样检查原文、链接、发布时间和脱敏结果。
10. Warehouse 保存结构化记录，Report 层按公司、产品、渠道、情感、问题类型聚合。

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
- 分析存储：DuckDB 起步，Postgres + pgvector 或 ClickHouse 进入规模化。
- 报告：Notebook、Metabase、Superset 或静态 Markdown 报告。
