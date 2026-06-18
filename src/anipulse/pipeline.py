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
from .sources import XApiSource, XSampleSource


@dataclass(frozen=True)
class PipelineResult:
    drafts: list[ContentDraft]
    notion_page_ids: list[str]
    resend_email_id: str | None = None
    resend_skipped_reason: str | None = None


class AniPulsePipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(
        self,
        dry_run: bool,
        limit: int | None = None,
        write_notion: bool | None = None,
        send_email: bool | None = None,
    ) -> PipelineResult:
        samples = self._load_samples()
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

        should_write_notion = (not dry_run) if write_notion is None else write_notion
        should_send_email = (not dry_run) if send_email is None else send_email

        notion_ids = NotionCalendarWriter(
            self.settings.notion_token,
            self.settings.notion_content_calendar_db_id,
            self.settings.notion_fallback_page_id,
        ).write(drafts, dry_run=not should_write_notion)

        email_result = ResendDigestMailer(
            self.settings.resend_api_key,
            self.settings.resend_from_email,
            self.settings.resend_to_email,
        ).send(drafts, enabled=should_send_email)

        return PipelineResult(
            drafts=drafts,
            notion_page_ids=notion_ids,
            resend_email_id=email_result.email_id,
            resend_skipped_reason=email_result.skipped_reason,
        )

    def _load_samples(self):
        if self.settings.source == "x-api":
            if not self.settings.x_bearer_token:
                raise RuntimeError("X_BEARER_TOKEN is required when ANIPULSE_SOURCE=x-api.")
            return XApiSource(
                bearer_token=self.settings.x_bearer_token,
                accounts=self.settings.x_accounts,
                tracked_titles=self.settings.tracked_titles,
                max_results=self.settings.x_max_results,
                lookback_hours=self.settings.x_lookback_hours,
            ).load()
        return XSampleSource(self.settings.source_file).load()
