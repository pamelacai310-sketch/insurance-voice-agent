from datetime import datetime, timezone

from insurance_voice_agent.schemas import InsuranceMention, SourceRef, build_content_hash


def test_content_hash_is_stable_after_whitespace_normalization() -> None:
    first = build_content_hash("Forum", "https://example.com/a", "Insurance   claim")
    second = build_content_hash("forum", "https://example.com/a", "insurance claim")
    assert first == second


def test_insurance_mention_validates_minimal_record() -> None:
    text = "理赔流程很慢，但客服最终帮我处理了。"
    source = SourceRef(
        platform="example_forum",
        source_type="forum",
        url="https://example.com/thread/1",
    )
    record = InsuranceMention(
        id_hash=build_content_hash(source.platform, str(source.url), text),
        source=source,
        published_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
        crawled_at=datetime(2026, 6, 5, tzinfo=timezone.utc),
        language="zh",
        redacted_text=text,
        product_category="health",
        sentiment_label="mixed",
        sentiment_score=-0.2,
        aspects=["claims", "customer_service"],
    )
    assert record.source.platform == "example_forum"
    assert record.aspects == ["claims", "customer_service"]
