from __future__ import annotations

import requests

from .models import ContentDraft


class ResendDigestMailer:
    def __init__(self, api_key: str | None, from_email: str | None, to_email: str | None) -> None:
        self.api_key = api_key
        self.from_email = from_email
        self.to_email = to_email

    def send(self, drafts: list[ContentDraft], dry_run: bool) -> None:
        if dry_run or not drafts:
            return
        if not self.api_key or not self.from_email or not self.to_email:
            return

        lines = "\n".join(draft.digest_line() for draft in drafts)
        requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": self.from_email,
                "to": [self.to_email],
                "subject": "AniPulse - recap des contenus planifies",
                "text": f"AniPulse a prepare {len(drafts)} contenu(s):\n\n{lines}",
            },
            timeout=20,
        ).raise_for_status()
