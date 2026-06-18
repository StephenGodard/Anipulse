from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import requests

from .models import XMetrics, XSample


class XSampleSource:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[XSample]:
        if not self.path.exists():
            raise FileNotFoundError(f"X samples file not found: {self.path}")

        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [XSample.model_validate(item) for item in payload]


class XApiSource:
    def __init__(
        self,
        bearer_token: str,
        accounts: list[str],
        tracked_titles: list[str],
        max_results: int,
    ) -> None:
        self.bearer_token = bearer_token
        self.accounts = accounts
        self.tracked_titles = tracked_titles
        self.max_results = max(5, min(max_results, 100))

    def load(self) -> list[XSample]:
        samples: list[XSample] = []
        for account in self.accounts:
            user_id = self._user_id(account)
            if not user_id:
                continue
            samples.extend(self._tweets(account, user_id))
        return samples

    def _user_id(self, username: str) -> str | None:
        response = requests.get(
            f"https://api.x.com/2/users/by/username/{username}",
            headers=self._headers(),
            timeout=20,
        )
        if response.status_code == 404:
            return None
        if response.status_code == 402:
            raise RuntimeError(
                "X API returned 402 Payment Required while resolving "
                f"@{username}. The token is valid, but the current X API plan "
                "does not allow this endpoint."
            )
        response.raise_for_status()
        return response.json().get("data", {}).get("id")

    def _tweets(self, username: str, user_id: str) -> list[XSample]:
        response = requests.get(
            f"https://api.x.com/2/users/{user_id}/tweets",
            headers=self._headers(),
            params={
                "max_results": self.max_results,
                "exclude": "retweets,replies",
                "tweet.fields": "created_at,public_metrics,attachments",
                "expansions": "attachments.media_keys",
                "media.fields": "type,url,preview_image_url",
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        media_keys = self._media_keys(payload)

        samples: list[XSample] = []
        for tweet in payload.get("data", []):
            titles = self._candidate_titles(tweet.get("text", ""))
            if not titles:
                continue

            metrics = tweet.get("public_metrics", {})
            samples.append(
                XSample(
                    source_account=username,
                    posted_at=self._created_at(tweet.get("created_at")),
                    text=tweet.get("text", ""),
                    candidate_titles=titles,
                    metrics=XMetrics(
                        likes=metrics.get("like_count", 0),
                        reposts=metrics.get("retweet_count", 0) + metrics.get("quote_count", 0),
                        replies=metrics.get("reply_count", 0),
                        views=metrics.get("impression_count", 0),
                    ),
                    media_count=len(media_keys.get(tweet.get("id"), [])),
                    url=f"https://x.com/{username}/status/{tweet.get('id')}",
                )
            )
        return samples

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.bearer_token}"}

    def _candidate_titles(self, text: str) -> list[str]:
        normalized = text.lower()
        return [title for title in self.tracked_titles if title.lower() in normalized]

    def _created_at(self, value: str | None) -> datetime:
        if not value:
            return datetime.now(timezone.utc)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _media_keys(self, payload: dict) -> dict[str, list[str]]:
        by_tweet: dict[str, list[str]] = {}
        for tweet in payload.get("data", []):
            keys = tweet.get("attachments", {}).get("media_keys", [])
            if keys:
                by_tweet[tweet.get("id")] = keys
        return by_tweet
