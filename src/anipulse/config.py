from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> None:
        return None


@dataclass(frozen=True)
class Settings:
    source: str
    source_file: Path
    export_dir: Path
    default_dry_run: bool
    daily_limit: int
    timezone: str
    animesphere_search_url: str
    x_bearer_token: str | None
    x_accounts: list[str]
    x_max_results: int
    x_lookback_hours: int
    tracked_titles: list[str]
    openai_api_key: str | None
    openai_model: str
    notion_token: str | None
    notion_content_calendar_db_id: str | None
    notion_fallback_page_id: str | None
    resend_api_key: str | None
    resend_from_email: str | None
    resend_to_email: str | None

    @property
    def can_write_notion(self) -> bool:
        return bool(self.notion_token and self.notion_content_calendar_db_id)

    @property
    def can_send_digest(self) -> bool:
        return bool(self.resend_api_key and self.resend_from_email and self.resend_to_email)


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        source=os.getenv("ANIPULSE_SOURCE", "sample"),
        source_file=Path(os.getenv("ANIPULSE_SOURCE_FILE", "data/x_samples.json")),
        export_dir=Path(os.getenv("ANIPULSE_EXPORT_DIR", "exports")),
        default_dry_run=_env_bool("ANIPULSE_DRY_RUN", default=True),
        daily_limit=int(os.getenv("ANIPULSE_DAILY_LIMIT", "4")),
        timezone=os.getenv("ANIPULSE_TIMEZONE", "Europe/Paris"),
        animesphere_search_url=os.getenv(
            "ANIMESPHERE_SEARCH_URL",
            "https://animesphere.io/api/anime/search?pageNumber=1&pageSize=50&title=",
        ),
        x_bearer_token=os.getenv("X_API_TOKEN") or os.getenv("X_BEARER_TOKEN") or None,
        x_accounts=_env_list("X_ACCOUNTS", default="shirotaku_fr,Tokanim_FR,gaak_fr,animotaku_fr"),
        x_max_results=int(os.getenv("X_MAX_RESULTS", "10")),
        x_lookback_hours=int(os.getenv("X_LOOKBACK_HOURS", "24")),
        tracked_titles=_env_list(
            "ANIPULSE_TRACKED_TITLES",
            default="Re:Zero,Classroom of the Elite,Black Clover,Marriagetoxin,MARRIAGE TOXIN",
        ),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        notion_token=os.getenv("NOTION_TOKEN") or None,
        notion_content_calendar_db_id=os.getenv("NOTION_CONTENT_CALENDAR_DB_ID") or None,
        notion_fallback_page_id=os.getenv("NOTION_FALLBACK_PAGE_ID") or None,
        resend_api_key=os.getenv("RESEND_API_KEY") or None,
        resend_from_email=os.getenv("RESEND_FROM_EMAIL") or None,
        resend_to_email=os.getenv("RESEND_TO_EMAIL") or None,
    )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_list(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]
