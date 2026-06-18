from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


Platform = Literal["SEO", "TikTok", "X / Twitter", "Instagram"]
ContentType = Literal[
    "SEO anime comme",
    "Article anime saison",
    "Script TikTok",
    "React X",
    "Thread X",
    "Reel Instagram",
]


class XMetrics(BaseModel):
    likes: int = 0
    reposts: int = 0
    replies: int = 0
    views: int = 0


class XSample(BaseModel):
    source_account: str
    posted_at: datetime
    text: str
    candidate_titles: list[str] = Field(default_factory=list)
    metrics: XMetrics = Field(default_factory=XMetrics)
    media_count: int = 0
    url: str | None = None


class AnimeMatch(BaseModel):
    title: str
    public_url: str
    raw: dict = Field(default_factory=dict)


class TrendCandidate(BaseModel):
    sample: XSample
    anime: AnimeMatch
    score: float
    reasons: list[str]


class ContentDraft(BaseModel):
    platform: Platform
    content_type: ContentType
    title: str
    anime_title: str
    anime_url: str
    source_url: str | None = None
    scheduled_at: datetime
    angle: str
    draft: str
    visual_note: str | None = None
    validation_status: str = "A valider"

    def digest_line(self) -> str:
        return f"- {self.platform} | {self.anime_title} | {self.title}"
