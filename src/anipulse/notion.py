from __future__ import annotations

import requests

from .models import ContentDraft


class NotionCalendarWriter:
    def __init__(
        self,
        token: str | None,
        database_id: str | None,
        fallback_page_id: str | None = None,
    ) -> None:
        self.token = token
        self.database_id = database_id
        self.fallback_page_id = fallback_page_id

    def write(self, drafts: list[ContentDraft], dry_run: bool) -> list[str]:
        if dry_run:
            return []
        if not self.token or not (self.database_id or self.fallback_page_id):
            raise RuntimeError("Notion credentials are required when dry-run is disabled.")

        page_ids: list[str] = []
        for draft in drafts:
            response = self._post_page(self._database_payload(draft)) if self.database_id else None
            if response is None or response.status_code >= 400:
                if not self.fallback_page_id:
                    if response is not None:
                        response.raise_for_status()
                    raise RuntimeError("Notion database is unavailable and no fallback page is configured.")
                response = self._post_page(self._fallback_payload(draft))
            response.raise_for_status()
            page_ids.append(response.json()["id"])

        return page_ids

    def _post_page(self, payload: dict) -> requests.Response:
        return requests.post(
            "https://api.notion.com/v1/pages",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Notion-Version": "2025-09-03",
            },
            json=payload,
            timeout=20,
        )

    def _database_payload(self, draft: ContentDraft) -> dict:
        return {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Nom": {"title": [{"text": {"content": draft.title}}]},
                "Plateformes": {"multi_select": [{"name": draft.platform}]},
                "Type contenu": {"select": {"name": draft.content_type}},
                "Validation": {"select": {"name": draft.validation_status}},
                "Lien AnimeSphere": {"url": draft.anime_url},
                "Lien source": {"url": draft.source_url},
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

    def _fallback_payload(self, draft: ContentDraft) -> dict:
        return {
            "parent": {"page_id": self.fallback_page_id},
            "properties": {
                "title": {
                    "title": [
                        {"type": "text", "text": {"content": f"[AniPulse] {draft.title}"}}
                    ]
                }
            },
            "children": self._content_blocks(draft),
        }

    def _content_blocks(self, draft: ContentDraft) -> list[dict]:
        return [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Planning"}}]},
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": (
                                    f"Plateforme: {draft.platform}\n"
                                    f"Type: {draft.content_type}\n"
                                    f"Date: {draft.scheduled_at.isoformat()}\n"
                                    f"Statut: {draft.validation_status}\n"
                                    f"Anime: {draft.anime_title}\n"
                                    f"URL AnimeSphere: {draft.anime_url}"
                                )
                            },
                        }
                    ]
                },
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Angle"}}]},
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": draft.angle[:1900]}}]},
            },
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
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"Note visuelle: {draft.visual_note or 'A definir'}"},
                        }
                    ]
                },
            },
        ]
