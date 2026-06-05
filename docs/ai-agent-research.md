# AI Agent 同类实现调研

调研日期：2026-06-05

目标问题：其他 AI agent 或数据采集系统如何实现“跨平台收集用户评论并做情感/主题分析”这类能力，以及哪些模式适合保险评论近半年监测项目。

## 核心结论

1. 成熟实现不是“一个大模型直接浏览全网”，而是把任务拆成采集、解析、结构化、分析、通知/入库几个阶段。
2. Agent 的价值在于规划、选择工具、理解页面结构、处理边界案例和输出结构化结果；大规模稳定采集仍依赖队列、限速、重试、去重和状态存储。
3. 对评论类任务，必须把“评论是否来自近半年、是否为用户原声、是否重复、是否含 PII”作为一等校验项。
4. 动态网页可以用 browser agent 兜底，但成本和不稳定性高，不应作为所有来源的默认方案。
5. 结构化输出必须由 Pydantic/JSON Schema 这类 schema 校验，不能直接信任自由文本回答。

## 参考实现

| 参考 | 实现方式 | 对本项目的启发 |
| --- | --- | --- |
| Obsei | 将系统拆成 Observer、Analyzer、Informer。Observer 采集 tweets、Reddit 评论、Facebook 页面评论、App Store/Google Play 评论、Google News、网站文本等；Analyzer 做分类、情感、翻译、PII；Informer 写入数据存储或通知系统。 | 采用“采集器 + 分析器 + 输出器”的管道边界；每个来源保存状态，适合定时任务和增量抓取。 |
| Apify Social Media Comment Scraper | 以 Actor/API 形式抽取 Instagram、Facebook、TikTok 评论并输出结构化数据。 | 对难维护平台，优先考虑成熟 Actor/API，自己只做标准化和合规过滤。 |
| Apify Request Queue / Crawlee | 使用持久化 URL 队列、去重、重试、并发、代理、HTTP 与无头浏览器统一接口。 | 本项目需要持久化 frontier queue，保证近半年增量抓取可恢复、可分布式处理。 |
| LangChain Agents | Agent 由模型、工具、系统提示和结构化输出组成，可用 `response_format` 返回校验 schema。 | 适合作为 query planner、extractor、classifier 的编排层。 |
| Agno Web Extraction Agent | Firecrawl 获取页面，Pydantic 定义输出 schema，agent 按 fetch、analyze、extract、structure 流程整理网页。 | 页面级抽取应先获得干净页面文本，再用 schema 约束输出，不直接保存模型散文式总结。 |
| Pydantic AI | 用 Pydantic 构建 JSON schema 并校验模型返回结果，支持 native/prompted/tool output。 | 评论抽取、情感标签、来源元数据都应强制校验；校验失败进入重试或人工队列。 |
| browser-use | 将网站暴露给 AI agent 做浏览器自动化，适合点击、输入、翻页等交互。 | 仅用于 JS 重、分页复杂、评论需交互展开的来源；要有预算、超时和失败回退。 |
| AutoScraper paper | 用 LLM 生成可复用 scraper，利用 HTML 层级结构和相似页面提升适配性。 | 对论坛、新闻站等同构页面，可让 agent 先生成抽取规则，再批量执行，而不是每页都让 LLM 读。 |
| WebLists / BardeenAgent paper | Agent 先执行网页任务，再把执行转成可重复程序；通过通用 CSS selector 捕捉页面列表项。 | 对评论列表页，优先学习 repeatable selectors，并把 selector 版本化。 |
| Webscraper paper | 用多模态 LLM 和工具处理动态、交互式、index-content 架构页面。 | 对“列表页 -> 详情页 -> 评论区”的网站，分阶段处理索引页和内容页。 |

## 推荐实现模式

### 1. 多 agent 分工

- Source Planner Agent：扩展保险关键词、品牌词、产品词、投诉词，生成来源和查询计划。
- Compliance Gate Agent：过滤不允许抓取、需要登录、明显违反站点规则或隐私风险高的来源。
- Collector Agents：按来源执行 API、HTTP crawler、browser automation。
- Extraction Agent：识别评论文本、发布时间、上下文、作者公开标识和来源 URL。
- Normalization Agent：统一时间、语言、产品/公司实体、去重哈希。
- Analysis Agent：输出情感、方面标签、购买/投诉/理赔等意图标签。
- QA Agent：抽样比对页面证据，标记误抽、重复、时间不符合、PII 未脱敏。

### 2. 确定性优先，LLM 兜底

推荐顺序：

1. 官方 API 或合规数据接口。
2. 稳定 HTML/JSON 接口。
3. Crawlee/Playwright 类无头浏览器。
4. Browser agent 处理复杂交互。
5. LLM 用于结构理解和字段抽取，不用于无限制浏览。

### 3. 可复用抽取规则

对同一网站或页面模板，第一次由 agent 生成候选 CSS selector / XPath / JSON path，人工或自动验证后保存为 adapter 版本。之后批量抓取时优先执行规则，失败时再回退到 LLM。

### 4. 数据质量指标

- 覆盖：来源数、平台数、关键词覆盖、保险品类覆盖。
- 时效：近半年命中率、过期评论误入率。
- 准确：评论块抽取准确率、发布时间抽取准确率、来源 URL 可追溯率。
- 去重：重复率、跨平台转载识别率。
- 合规：PII 脱敏命中率、受限来源拦截率、robots/ToS 检查记录。

## Sources

- Obsei: https://github.com/obsei/obsei
- Apify Social Media Comment Scraper API: https://apify.com/automation-lab/social-media-sentiment/api
- Apify Request Queue docs: https://docs.apify.com/platform/storage/request-queue
- Crawlee Python introduction: https://crawlee.dev/python/docs/introduction
- LangChain Agents docs: https://docs.langchain.com/oss/python/langchain/agents
- Agno Web Extraction Agent: https://docs.agno.com/cookbook/agents/web-extraction-agent
- Pydantic AI structured output: https://pydantic.dev/docs/ai/core-concepts/output/
- browser-use: https://github.com/browser-use/browser-use
- AutoScraper: https://arxiv.org/abs/2404.12753
- WebLists / BardeenAgent: https://arxiv.org/abs/2504.12682
- Webscraper MLLM framework: https://arxiv.org/abs/2603.29161
