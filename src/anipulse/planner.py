from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from .models import ContentDraft, ContentType, Platform, TrendCandidate


CONTENT_SLOTS: list[tuple[Platform, ContentType, time]] = [
    ("SEO", "Article anime saison", time(9, 30)),
    ("TikTok", "Script TikTok", time(12, 15)),
    ("X / Twitter", "React X", time(18, 30)),
    ("X / Twitter", "React X", time(21, 15)),
]


class ContentPlanner:
    def __init__(self, timezone: str) -> None:
        self.timezone = ZoneInfo(timezone)

    def plan(self, candidates: list[TrendCandidate], limit: int) -> list[ContentDraft]:
        today = datetime.now(self.timezone).date()
        selected = candidates[:limit]
        drafts: list[ContentDraft] = []

        for index, candidate in enumerate(selected):
            platform, content_type, slot = CONTENT_SLOTS[index % len(CONTENT_SLOTS)]
            scheduled_at = datetime.combine(today + timedelta(days=index // 4), slot, self.timezone)
            drafts.append(
                ContentDraft(
                    platform=platform,
                    content_type=content_type,
                    title=self._title(platform, candidate.anime.title),
                    anime_title=candidate.anime.title,
                    anime_url=candidate.anime.public_url,
                    source_url=candidate.sample.url,
                    scheduled_at=scheduled_at,
                    angle=self._angle(platform, candidate),
                    draft="",
                    visual_note=self._visual_note(candidate),
                )
            )

        return drafts

    def _title(self, platform: Platform, anime_title: str) -> str:
        if platform == "SEO":
            return f"Pourquoi regarder {anime_title} cette saison ?"
        if platform == "TikTok":
            return f"Script TikTok - {anime_title}"
        return f"React X - {anime_title}"

    def _angle(self, platform: Platform, candidate: TrendCandidate) -> str:
        if platform == "SEO":
            return "Transformer la hype du moment en page d'acquisition AnimeSphere."
        if platform == "TikTok":
            return "Donner envie de lancer l'anime en partant d'un signal fort de la communaute."
        return "React chaud, fan, court et communautaire autour de l'anime."

    def _visual_note(self, candidate: TrendCandidate) -> str:
        return f"S'inspirer du post source: {candidate.sample.media_count} visuel(s), compte @{candidate.sample.source_account}."
