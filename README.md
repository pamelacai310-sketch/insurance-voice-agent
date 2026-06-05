# Insurance Voice Agent

面向保险行业的公开用户评论采集与分析项目。项目目标是持续网罗全网公开渠道中，近半年用户对保险产品、保险公司、代理人服务、理赔、退保、保费、免责条款等主题的真实评论，并沉淀为可追溯、可去重、可分析的数据资产。

本仓库初始化日期为 2026-06-05，因此首个默认观察窗口是 2025-12-05 至 2026-06-05。后续运行时应按任务执行日动态回推 6 个月。

## 当前状态

这是项目的研究与工程骨架版本，包含：

- AI agent 与社媒/评论监听同类实现调研
- 保险评论采集的候选架构
- 数据字段与校验模型
- 来源策略、覆盖指标与合规边界
- 后续实现路线图

当前仓库不包含任何实际抓取的用户评论数据。

## 设计结论

调研后建议采用混合式架构：

- 对可通过 API 或稳定 HTML 获取的站点，优先使用确定性采集器。
- 对动态页面、评论折叠、分页、站内搜索等复杂交互，使用 browser agent 作为兜底。
- LLM agent 主要负责查询规划、页面结构理解、评论块抽取、主题/情感/方面标签，而不是直接替代所有爬虫逻辑。
- 所有抽取结果必须进入结构化 schema 校验、去重、时间窗口过滤、PII 脱敏和人工抽样审计。
- 采集队列必须有持久化状态，支持增量抓取、失败重试、限速和来源覆盖统计。

## 推荐流水线

```text
source planner
  -> compliance gate
  -> persistent frontier queue
  -> API / crawler / browser collectors
  -> comment extractor
  -> normalization and dedupe
  -> sentiment and aspect analyzer
  -> quality audit
  -> warehouse and reports
```

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## 文档入口

- [AI agent 实现调研](docs/ai-agent-research.md)
- [消费者智能方法接入研究](docs/method-integration-study.md)
- [系统架构](docs/architecture.md)
- [数据 Schema](docs/data-schema.md)
- [来源策略](docs/source-strategy.md)
- [合规边界](docs/compliance.md)

## 下一阶段

1. 建立保险关键词词库与品牌/产品实体词库。
2. 实现搜索发现器，按近半年时间窗口生成候选 URL。
3. 实现首批公开来源连接器：新闻评论、论坛、问答、视频评论、应用商店评论。
4. 接入 LLM 结构化抽取与情感/方面分类。
5. 建立抽样评估集，度量召回、重复率、时间过滤准确率和 PII 脱敏准确率。
