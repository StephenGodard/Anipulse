from __future__ import annotations

from dataclasses import dataclass
from html import escape

import requests

from .models import ContentDraft


@dataclass(frozen=True)
class EmailResult:
    email_id: str | None
    skipped_reason: str | None = None


class ResendDigestMailer:
    def __init__(self, api_key: str | None, from_email: str | None, to_email: str | None) -> None:
        self.api_key = api_key
        self.from_email = from_email
        self.to_email = to_email

    def send(self, drafts: list[ContentDraft], enabled: bool) -> EmailResult:
        if not enabled:
            return EmailResult(email_id=None, skipped_reason="disabled")
        if not drafts:
            return EmailResult(email_id=None, skipped_reason="no drafts")
        if not self.api_key or not self.from_email or not self.to_email:
            return EmailResult(email_id=None, skipped_reason="missing Resend configuration")

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": self.from_email,
                "to": [self.to_email],
                "subject": f"AniPulse - {len(drafts)} contenu(s) planifie(s) a valider",
                "text": self._text(drafts),
                "html": self._html(drafts),
            },
            timeout=20,
        )
        response.raise_for_status()
        return EmailResult(email_id=response.json().get("id"))

    def _text(self, drafts: list[ContentDraft]) -> str:
        lines = ["AniPulse a prepare les contenus suivants:", ""]
        for draft in drafts:
            lines.extend(
                [
                    draft.digest_line(),
                    f"Date: {draft.scheduled_at.isoformat()}",
                    f"AnimeSphere: {draft.anime_url}",
                    f"Statut: {draft.validation_status}",
                    "",
                ]
            )
        return "\n".join(lines)

    def _html(self, drafts: list[ContentDraft]) -> str:
        items = []
        for draft in drafts:
            items.append(
                "<li>"
                f"<strong>{escape(draft.platform)}</strong> - {escape(draft.title)}<br>"
                f"Anime: {escape(draft.anime_title)}<br>"
                f"Date: {escape(draft.scheduled_at.isoformat())}<br>"
                f"Statut: {escape(draft.validation_status)}<br>"
                f"<a href=\"{escape(draft.anime_url)}\">Fiche AnimeSphere</a>"
                "</li>"
            )
        return (
            "<h1>AniPulse - contenus a valider</h1>"
            "<p>Voici le recap des contenus generes et planifies.</p>"
            f"<ul>{''.join(items)}</ul>"
        )
