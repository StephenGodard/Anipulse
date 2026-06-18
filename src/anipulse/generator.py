from __future__ import annotations

import requests

from .models import ContentDraft


class ContentGenerator:
    def __init__(self, api_key: str | None, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, drafts: list[ContentDraft]) -> list[ContentDraft]:
        return [draft.model_copy(update={"draft": self._generate_one(draft)}) for draft in drafts]

    def _generate_one(self, draft: ContentDraft) -> str:
        if not self.api_key:
            return self._fallback(draft)

        prompt = self._prompt(draft)
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": [
                    {
                        "role": "system",
                        "content": "Tu es AniPulse, un agent de content factory anime. Ton style X/TikTok est fan, react, communautaire, naturel, jamais corporate. Les liens AnimeSphere servent a decouvrir l'anime, pas a forcer une promotion.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.8,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return self._extract_text(payload) or self._fallback(draft)

    def _prompt(self, draft: ContentDraft) -> str:
        return (
            f"Genere un brouillon pour {draft.platform}.\n"
            f"Type: {draft.content_type}\n"
            f"Anime: {draft.anime_title}\n"
            f"URL AnimeSphere: {draft.anime_url}\n"
            f"Angle: {draft.angle}\n"
            f"Note visuelle: {draft.visual_note}\n"
            "Contraintes: francais, ton fan anime, pas de spoiler majeur, CTA discret."
        )

    def _extract_text(self, payload: dict) -> str | None:
        if isinstance(payload.get("output_text"), str):
            return payload["output_text"]

        chunks: list[str] = []
        for output in payload.get("output", []):
            for content in output.get("content", []):
                text = content.get("text")
                if isinstance(text, str):
                    chunks.append(text)
        return "\n".join(chunks).strip() or None

    def _fallback(self, draft: ContentDraft) -> str:
        if draft.platform == "X / Twitter":
            return (
                f"{draft.anime_title} est en train de faire parler et franchement je comprends la hype.\n\n"
                f"Si tu veux le retrouver facilement: {draft.anime_url}"
            )
        if draft.platform == "TikTok":
            return (
                f"Hook: Tu cherches un anime qui fait vraiment parler en ce moment ?\n"
                f"Corps: {draft.anime_title}, c'est clairement le genre de titre que la commu commence a pousser fort.\n"
                f"CTA: Va voir sa fiche AnimeSphere pour savoir ou le regarder: {draft.anime_url}"
            )
        return (
            f"# Pourquoi regarder {draft.anime_title} cette saison ?\n\n"
            f"{draft.anime_title} ressort dans les discussions anime du moment. "
            f"L'article doit expliquer pourquoi la hype monte, a qui l'anime peut plaire, "
            f"et renvoyer vers la fiche AnimeSphere: {draft.anime_url}"
        )
