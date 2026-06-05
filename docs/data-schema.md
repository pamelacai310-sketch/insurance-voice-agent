# 数据 Schema

本项目的基本单位是“保险相关用户评论提及”，对应代码中的 `InsuranceMention`。

## 关键字段

| 字段 | 含义 |
| --- | --- |
| `id_hash` | 基于平台、URL、规范化文本生成的稳定哈希 |
| `source.platform` | 来源平台，例如 Reddit、YouTube、知乎、微博、新闻站评论区等 |
| `source.source_type` | 来源类型，例如 forum、video_comment、review_site、news_comment |
| `source.url` | 可追溯的评论或页面 URL |
| `published_at` | 评论发布时间 |
| `crawled_at` | 系统采集时间 |
| `language` | 文本语言 |
| `country_region` | 来源地区或目标市场，未知则为空 |
| `raw_text` | 原始文本，可选；生产环境可只短期保存 |
| `redacted_text` | 脱敏后的文本，分析优先使用该字段 |
| `insurer_names` | 识别到的保险公司 |
| `product_names` | 识别到的产品名 |
| `product_category` | 保险品类 |
| `sentiment_label` | positive、negative、neutral、mixed、unknown |
| `sentiment_score` | -1 到 1 的连续情感分 |
| `aspects` | 理赔、保费、免责、续保、代理人等方面标签 |
| `intent` | 投诉、咨询、购买考虑、经验分享、表扬等意图 |
| `risk_flags` | PII、疑似广告、疑似水军、法律风险等标记 |
| `duplicate_of` | 如为重复内容，指向主记录哈希 |
| `model_trace_id` | 结构化抽取或分析模型的运行追踪 ID |

## 原则

- `redacted_text` 是下游分析默认字段。
- `raw_text` 不应进入公开仓库，不应长期保存。
- 每条记录必须有来源 URL 和发布时间；无法确定发布时间的记录进入人工复核或低置信队列。
- 所有枚举标签需要版本化，避免模型升级后口径不可比。
