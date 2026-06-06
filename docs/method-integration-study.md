# 消费者智能方法接入研究

调研日期：2026-06-05

问题：用户提供的“市场智能、舆情监测与用户体验研究”方法中，哪些可以结合到 `insurance-voice-agent`，以及应放在项目的哪个阶段。

结论先行：本项目的核心目标是近半年公开保险评论采集、结构化抽取、主题/情感分析和可追溯报告。因此最值得立即接入的是 `last30days-skill` / `last30days-skill-cn` 的 30 天实时脉冲层、`LangExtract`、`BERTopic`、受合规约束的 `ScrapeGraphAI/Markdownify` 思路、结构化提示约束、可替换模型路由，以及 `GPT Researcher` 风格的定期研究报告。`Formbricks`、`PostHog/OpenReplay`、`Qwen2.5-VL` 可以作为第二阶段扩展。`VibeVoice` 和 `WebGazer.js` 只适合特定 VoC/UX 子项目，不应进入当前主干采集链路。

## 采用分级

| 分级 | 方法 | 结论 |
| --- | --- | --- |
| 立即采用 | last30days-skill、last30days-skill-cn、LangExtract、BERTopic、结构化提示约束、模型路由、ScrapeGraphAI 的 Markdown/结构化抽取思路 | 直接增强实时发现、评论抽取、证据定位、主题发现和报告可信度。 |
| 近期试点 | GPT Researcher、STORM/Co-STORM、Qwen2.5-VL、Formbricks、n8n | 适合做报告生成、深度专题研究、视觉证据、主动问卷和外部编排。 |
| 后续扩展 | PostHog、OpenReplay、VibeVoice | 取决于项目是否建设用户端产品、内部研究平台或接入客服音频。 |
| 暂不接入 | WebGazer.js、商业 SaaS 型 Buska/Brand24/BuzzSumo/Octolens 作为核心依赖 | 与当前“公开评论监测”目标不直接匹配；可作为竞品能力参照。 |
| 明确不采用 | 绕过验证码、登录、付费墙、robots/ToS 或反爬检测的隐蔽采集 | 与项目合规边界冲突。 |

## 方法评估矩阵

| 方法 | 可接入位置 | 对保险评论项目的价值 | 主要限制 | 决策 |
| --- | --- | --- | --- | --- |
| Qwen3-235B-A22B、DeepSeek-V3 等 MoE LLM | `model_router`、`extractor`、`analyzer`、`reporter` | 中文保险评论语义复杂，强推理模型适合长评论、隐性投诉、销售误导、免责条款争议识别。 | 大模型自托管成本高；不同提供商的隐私、延迟和价格差异明显。 | 做成可替换模型接口，不把任何单一模型写死为核心依赖。 |
| Qwen2.5-VL-72B-Instruct | `multimodal_evidence_parser` | 能处理截图、图文评论、App Store 截图、短视频帧、产品页面截图中的表格和布局。 | 当前主目标是文本评论；视觉模型成本高，需要证据脱敏。 | 二阶段试点，用于“图文投诉/保单截图/视频评论摘要”场景。 |
| GPT Researcher | `research_reporter` | 适合每周/月自动生成“保险舆情专题报告”，把采集到的内部数据与公开资料结合，输出带引用的背景研究。 | 不适合作为高频评论采集器；多 agent 模式成本高。 | 近期接入 PIP/CLI 形态，作为离线报告生成器。 |
| STORM / Co-STORM | `topic_deep_dive` | 对 BERTopic 发现的异常主题做多视角追问，例如“医疗险续保争议”“重疾险理赔拒赔”专题。 | 学术式知识策展较重，不适合日常批量流水线。 | 先不进主链路，作为高价值主题的人工触发深度研究工具。 |
| 结构化提示工程 | `prompts/`、`reporter`、`qa_auditor` | 强制输出 `[Missing]`、`[Stale]`、`[Assumption]`，降低报告幻觉；特别适合保险监管和产品条款场景。 | 需要版本化 prompt，且输出仍需 schema 校验。 | 立即采用，并纳入 QA 评估。 |
| ScrapeGraphAI / SmartScraper / Markdownify | `collector_fallback`、`parser` | 对动态或结构混乱页面，先转 Markdown 或结构化 JSON，再交给抽取器，可减少手写解析规则。 | API 成本和外部依赖；报告中提到的 stealth/绕过检测做法不可采用。 | 只采用“公开页面清洗和结构化抽取”能力，禁止绕过访问控制。 |
| n8n | `orchestration`、`alerting` | 可用定时任务、Slack/邮件/表格节点快速搭建舆情预警和人工复核流程。 | 不应替代核心 Python 数据管道；工作流版本管理要额外治理。 | 可作为部署层可选项，不进入核心库依赖。 |
| last30days-skill | `real_time_signal_probe`、`comparative_pulse_report` | 并行研究 Reddit、X/Twitter、YouTube、TikTok、Hacker News、Polymarket、GitHub、Web 等近 30 天公开讨论，按互动指标生成带引用的实时舆情和竞品对比信号。 | 输出是候选信号和综合摘要，不是完整评论主库；部分平台依赖 API key、浏览器会话或外部服务。 | 立即采用为 30 天实时脉冲层，结果必须经合规门和主采集链路验证后才可沉淀。 |
| last30days-skill-cn | `real_time_signal_probe_cn`、`china_market_signal_probe` | 覆盖微博、小红书、B站、知乎、抖音、微信公众号、百度、今日头条等中文平台，适合中国市场保险口碑、投诉、竞品和购买决策热点发现。 | 中文平台访问规则差异大，cookie/session 或爬虫模式必须单独审批；互动指标容易受平台机制影响。 | 中国市场优先试点来源，优先官方 API 或允许的公开页面。 |
| BERTopic | `topic_modeler`、`trend_detector` | 把大量保险评论聚类为可解释主题，并用 topics-over-time 跟踪近半年主题变化。 | 中文 embedding、短文本噪声、聚类稳定性需要调参和抽样审计。 | 立即采用，作为第一阶段核心分析模块。 |
| Formbricks | `survey_trigger`、`active_voc` | 当公开评论发现异常主题后，向自有用户或研究样本发定向问卷，验证原因。 | 只适合自有用户/许可样本，不能用于抓取公开评论。 | 二阶段接入，形成“被动舆情 -> 主动问卷”闭环。 |
| VibeVoice | `voice_ingestion` | 如果后续接入客服录音或访谈音频，可把语音转文字再进入同一套抽取/主题模型。 | 当前项目没有音频源；客服录音通常涉及高敏个人信息和同意管理。 | 后续扩展，不进入当前 MVP。 |
| Google LangExtract | `extractor`、`qa_auditor` | 强项是结构化抽取和来源定位，适合把评论文本映射到原文 span，便于审计和人工复核。 | 仍需模型选择和 few-shot 示例；中文保险标签需自定义。 | 立即采用，优先于自由文本式 LLM 抽取。 |
| PostHog | `product_analytics` | 如果项目后续有仪表板或内部标注平台，可追踪分析员行为、漏斗、会话回放和实验。 | 与全网评论采集无直接关系；自托管和数据保留需要治理。 | 平台化后再接入。 |
| OpenReplay | `ux_replay` | 比 PostHog 更聚焦自托管会话回放和调试，可用于标注后台/报告系统 UX 改进。 | 只监测自有产品，不监测外部舆情。 | 平台化后作为 PostHog 替代或补充。 |
| WebGazer.js | `ux_lab` | 可在用户明确授权的研究实验中收集视线热点，评估保险报告或 H5 页面可读性。 | 生物特征风险高；官方仓库提示维护不再保证；与评论采集主目标弱相关。 | 不进主干，仅保留为独立 UX 实验选项。 |
| Buska / Octolens / Brand24 / BuzzSumo | `benchmarking` | 可借鉴线索评分、Share of Voice、KOL 识别、内容热点发现等产品能力。 | 多数为商业 SaaS，不符合“自有开源项目核心能力”定位。 | 只做竞品能力参考。 |

## 推荐接入后的目标架构

```text
seed taxonomy
  -> last30days pulse
  -> candidate signals
  -> compliance gate
  -> source planner
  -> frontier queue
  -> collectors
       -> api / crawlee / playwright
       -> public-page markdownifier
       -> browser fallback
  -> evidence store
  -> grounded extractor
       -> LangExtract / Pydantic schema
  -> normalization and dedupe
  -> analysis
       -> sentiment and aspect classifier
       -> BERTopic topic modeler
       -> topics-over-time trend detector
  -> QA auditor
  -> reports
       -> weekly GPT Researcher-style report
       -> STORM-style deep dive for flagged topics
  -> optional feedback loop
       -> Formbricks targeted survey
       -> PostHog/OpenReplay for internal product UX
```

## 优先实现路线

### Phase 1：文本智能主链路

目标：先把“公开文本评论”做准。

- 增加 `real_time_signal_probe` 路线图：用 `last30days-skill` 和 `last30days-skill-cn` 发现最近 30 天保险热点、竞品对比、平台信号和高互动用户之声。
- 定义 `SignalPromotionPolicy`：实时信号进入近半年主库前必须通过来源可追溯、时间过滤、去重、PII 检查和人工抽样。
- 增加 `model_router`：支持 OpenAI-compatible API、本地 Ollama/vLLM、云端 provider。
- 增加 `grounded_extractor`：以 `LangExtract` 或同类 span grounding 方式输出 `InsuranceMention`。
- 增加 prompt 合同：所有报告必须显式标记 `[Missing]`、`[Stale]`、`[Assumption]`。
- 增加 `topic_modeler`：用 BERTopic 聚类，并按周/月生成 `topics_over_time`。
- 增加人工审计样本：抽样检查抽取 span、发布时间、情感和主题标签。

### Phase 2：报告与深度研究

目标：把评论数据转成可读市场智能。

- GPT Researcher 用于周报/月报，不负责原始评论抓取。
- STORM/Co-STORM 用于 BERTopic 发现的高风险主题深挖。
- 报告模板加入来源矩阵、时间窗口、样本数、重复率、争议点和未证实假设。

### Phase 3：主动 VoC 闭环

目标：用自有样本验证公开舆情。

- 当某个主题异常上升时，自动生成 Formbricks 问卷草稿。
- 问卷结果作为单独来源类型进入 warehouse，和公开评论分开标记。
- 如果建设内部标注/仪表板，再接入 PostHog 或 OpenReplay 做产品分析。

### Phase 4：多模态与语音

目标：扩展到截图、视频和客服语音，但不影响文本 MVP。

- Qwen2.5-VL 处理公开图文评论、产品页面截图和视频帧摘要。
- VibeVoice 或其他 ASR 只在有合法授权的访谈/客服音频场景启用。
- WebGazer.js 只用于独立、明示同意的 UX 实验，不采集到主评论库。

## 合规约束

这些做法不应接入项目：

- 绕过验证码、登录、付费墙、访问控制或平台明确禁止的自动化限制。
- 保存未脱敏的手机号、身份证号、保单号、详细地址、邮箱等个人信息。
- 将 WebGazer.js 这类生物特征采集工具默认嵌入公开产品。
- 把商业 SaaS 抓取结果与自采公开评论混在同一来源类型中，导致来源不可追溯。
- 把 GPT Researcher/STORM 的综合推断当作用户原始评论。
- 把 `last30days` 的互动权重当作事实结论，或未经验证直接写入近半年主库。

## 30 天脉冲预留对象

| 对象 | 类型 | 用途 |
| --- | --- | --- |
| `RealTimeSignalProbe` | Workflow config | 一次 30 天实时研究任务，记录查询词、平台范围、运行时间和输出路径。 |
| `RealTimeSignal` | Schema | 单个平台或来源返回的候选信号，包含 topic、platform、source_url、published_at、observed_at、engagement_metrics、summary、citations。 |
| `ComparativePulseReport` | Schema | 竞品对比输出，包含 competitors、strengths、weaknesses、source_counts、engagement_weighted_findings。 |
| `SignalPromotionPolicy` | Policy config | 定义哪些实时信号可进入近半年主库，以及验证、脱敏和审计要求。 |

## 需要新增的工程对象

| 对象 | 类型 | 用途 |
| --- | --- | --- |
| `ModelRouter` | Python interface | 根据任务选择低成本分类模型、长上下文模型或强推理模型。 |
| `GroundedExtraction` | Schema | 保存字段值和原文 span，支持人工审计。 |
| `TopicSnapshot` | Schema | 保存 topic id、关键词、代表评论、时间桶、趋势分数。 |
| `ResearchReport` | Schema | 保存报告版本、输入样本、引用、缺失项、假设项。 |
| `SurveyTrigger` | Workflow config | 将异常主题转化为 Formbricks 问卷任务。 |
| `EvidencePolicy` | Config | 控制原文、截图、音频、视频的保留期限和脱敏策略。 |

## Sources

- GPT Researcher docs: https://docs.gptr.dev/
- GPT Researcher how-to-choose: https://docs.gptr.dev/docs/gpt-researcher/getting-started/how-to-choose
- GPT Researcher GitHub: https://github.com/assafelovic/gpt-researcher
- STORM GitHub: https://github.com/stanford-oval/storm
- ScrapeGraphAI docs: https://docs.scrapegraphai.com/
- BERTopic representation docs: https://maartengr.github.io/BERTopic/getting_started/representation/representation.html
- BERTopic dynamic topic modeling: https://maartengr.github.io/BERTopic/getting_started/topicsovertime/topicsovertime.html
- Formbricks GitHub: https://github.com/formbricks/formbricks
- PostHog GitHub: https://github.com/posthog/posthog
- OpenReplay GitHub: https://github.com/openreplay/openreplay
- WebGazer GitHub: https://github.com/brownhci/WebGazer
- Google LangExtract GitHub: https://github.com/google/langextract
- Microsoft VibeVoice GitHub: https://github.com/microsoft/VibeVoice
- n8n docs: https://docs.n8n.io/
- Qwen3-235B-A22B-Instruct-2507 model card: https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507
- Qwen2.5-VL-72B-Instruct model card: https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct
- DeepSeek-V3 GitHub: https://github.com/deepseek-ai/DeepSeek-V3
- last30days-skill GitHub: https://github.com/mvanhorn/last30days-skill
- last30days-skill-cn GitHub: https://github.com/Jesseovo/last30days-skill-cn
