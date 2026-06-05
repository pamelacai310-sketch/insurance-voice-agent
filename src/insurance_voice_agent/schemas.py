"""Structured records produced by collectors and extraction agents."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator

SourceType = Literal[
    "social",
    "forum",
    "review_site",
    "news_comment",
    "video_comment",
    "qna",
    "complaint_portal",
    "app_store",
    "search_result",
    "other",
]

SentimentLabel = Literal["positive", "negative", "neutral", "mixed", "unknown"]

ProductCategory = Literal[
    "life",
    "health",
    "critical_illness",
    "annuity",
    "auto",
    "property",
    "travel",
    "accident",
    "commercial",
    "unknown",
]

AspectLabel = Literal[
    "claims",
    "sales",
    "premium",
    "coverage",
    "exclusion",
    "renewal",
    "customer_service",
    "agent",
    "app",
    "surrender",
    "fraud_risk",
    "regulatory",
    "other",
]


def normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())


def build_content_hash(platform: str, url: str, text: str) -> str:
    normalized = normalize_text(text)
    payload = f"{platform.casefold()}|{url}|{normalized}"
    return sha256(payload.encode("utf-8")).hexdigest()


class SourceRef(BaseModel):
    platform: str = Field(min_length=1, description="Public source platform name.")
    source_type: SourceType
    url: HttpUrl
    thread_url: Optional[HttpUrl] = None
    title: Optional[str] = None


class InsuranceMention(BaseModel):
    id_hash: str = Field(min_length=32)
    source: SourceRef
    published_at: datetime
    crawled_at: datetime
    language: str = Field(default="unknown", min_length=2, max_length=16)
    country_region: Optional[str] = None
    raw_text: Optional[str] = Field(default=None, description="Short-lived raw evidence.")
    redacted_text: str = Field(min_length=1, description="PII-redacted text for analysis.")
    author_hash: Optional[str] = None
    author_public_handle: Optional[str] = None
    insurer_names: list[str] = Field(default_factory=list)
    product_names: list[str] = Field(default_factory=list)
    product_category: ProductCategory = "unknown"
    sentiment_label: SentimentLabel = "unknown"
    sentiment_score: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    aspects: list[AspectLabel] = Field(default_factory=list)
    intent: Optional[str] = None
    risk_flags: list[str] = Field(default_factory=list)
    duplicate_of: Optional[str] = None
    model_trace_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("redacted_text")
    @classmethod
    def redacted_text_must_not_be_blank(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("redacted_text must not be blank")
        return normalized

    @field_validator("id_hash", "author_hash", "duplicate_of", mode="after")
    @classmethod
    def hashes_should_be_lower_hex(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        lowered = value.lower()
        if any(char not in "0123456789abcdef" for char in lowered):
            raise ValueError("hash fields must be lowercase hexadecimal")
        return lowered
