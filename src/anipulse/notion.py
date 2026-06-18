from __future__ import annotations

import requests

from .models import ContentDraft


class NotionCalendarWriter:
    def __init__(self, token: str | None, database_id: str | None) -> None:
        self.token = token
        self.database_id = database_id

    def write(self, drafts: list[ContentDraft], dry_run: bool) -> list[str]:
        if dry_run:
            return []
        if not self.token or not self.database_id:
            raise RuntimeError("Notion credentials are required when dry-run is disabled.")

        page_ids: list[str] = []
        for draft in drafts:
            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "Notion-Version": "2022-06-28",
                },
                json=self._payload(draft),
                timeout=20,
            )
            response.raise_for_status()
            page_ids.append(response.json()["id"])

        return page_ids

    def _payload(self, draft: ContentDraft) -> dict:
        return {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Nom": {"title": [{"text": {"content": draft.title}}]},
                "Plateformes": {"multi_select": [{"name": draft.platform}]},
                "Type contenu": {"select": {"name": draft.content_type}},
                "Validation": {"select": {"name": draft.validation_status}},
                "Lien AnimeSphere": {"url": draft.anime_url},
                "Date": {"date": {"start": draft.scheduled_at.isoformat()}},
            },
            "children": [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Brouillon"}}]},
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": draft.draft[:1900]}}]},
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Angle: {draft.angle}"}}]},
                },
            ],
        }
