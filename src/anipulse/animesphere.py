from __future__ import annotations

from urllib.parse import quote

import requests

from .models import AnimeMatch


class AnimeSphereClient:
    def __init__(self, search_url: str) -> None:
        self.search_url = search_url

    def search_first(self, title: str) -> AnimeMatch | None:
        response = requests.get(f"{self.search_url}{quote(title)}", timeout=12)
        response.raise_for_status()
        payload = response.json()

        item = self._first_item(payload)
        if not item:
            return None

        public_url = self._public_url(item)
        anime_title = item.get("title") or item.get("name") or title
        if not public_url:
            return None

        return AnimeMatch(title=anime_title, public_url=public_url, raw=item)

    def _first_item(self, payload: object) -> dict | None:
        if isinstance(payload, list) and payload:
            return payload[0] if isinstance(payload[0], dict) else None
        if isinstance(payload, dict):
            for key in ("items", "results", "data", "anime"):
                value = payload.get(key)
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    return value[0]
            if payload.get("slug") or payload.get("url") or payload.get("publicUrl"):
                return payload
        return None

    def _public_url(self, item: dict) -> str | None:
        for key in ("publicUrl", "public_url", "url", "link"):
            value = item.get(key)
            if isinstance(value, str) and value.startswith("http"):
                return value

        slug = item.get("slug")
        if isinstance(slug, str) and slug:
            return f"https://animesphere.io/anime/{slug}"

        return None
