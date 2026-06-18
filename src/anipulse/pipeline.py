from __future__ import annotations

from dataclasses import dataclass

from .analyzer import TrendAnalyzer
from .animesphere import AnimeSphereClient
from .config import Settings
from .emailer import ResendDigestMailer
from .generator import ContentGenerator
from .models import ContentDraft
from .notion import NotionCalendarWriter
from .planner import ContentPlanner
from .sources import XSampleSource


@dataclass(frozen=True)
class PipelineResult:
    drafts: list[ContentDraft]
    notion_page_ids: list[str]


class AniPulsePipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, dry_run: bool, limit: int | None = None) -> PipelineResult:
        samples = XSampleSource(self.settings.source_file).load()
        animesphere = AnimeSphereClient(self.settings.animesphere_search_url)
        candidates = TrendAnalyzer(animesphere).analyze(samples)
        planned = ContentPlanner(self.settings.timezone).plan(
            candidates,
            limit or self.settings.daily_limit,
        )
        drafts = ContentGenerator(
            self.settings.openai_api_key,
            self.settings.openai_model,
        ).generate(planned)

        notion_ids = NotionCalendarWriter(
            self.settings.notion_token,
            self.settings.notion_content_calendar_db_id,
            self.settings.notion_fallback_page_id,
        ).write(drafts, dry_run=dry_run)

        ResendDigestMailer(
            self.settings.resend_api_key,
            self.settings.resend_from_email,
            self.settings.resend_to_email,
        ).send(drafts, dry_run=dry_run)

        return PipelineResult(drafts=drafts, notion_page_ids=notion_ids)
