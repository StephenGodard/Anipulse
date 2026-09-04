from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from .models import ContentDraft


@dataclass(frozen=True)
class ExportResult:
    json_path: Path
    markdown_path: Path


class DraftExporter:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def export(self, drafts: list[ContentDraft]) -> ExportResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        json_path = self.output_dir / f"anipulse-drafts-{stamp}.json"
        markdown_path = self.output_dir / f"anipulse-drafts-{stamp}.md"

        json_path.write_text(
            json.dumps([draft.model_dump(mode="json") for draft in drafts], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        markdown_path.write_text(self._markdown(drafts), encoding="utf-8")
        return ExportResult(json_path=json_path, markdown_path=markdown_path)

    def _markdown(self, drafts: list[ContentDraft]) -> str:
        lines = ["# AniPulse - brouillons generes", ""]
        for index, draft in enumerate(drafts, start=1):
            lines.extend(
                [
                    f"## {index}. {draft.title}",
                    "",
                    f"- Plateforme: {draft.platform}",
                    f"- Type: {draft.content_type}",
                    f"- Anime: {draft.anime_title}",
                    f"- URL AnimeSphere: {draft.anime_url}",
                    f"- Image anime: {draft.image_url or 'A definir'}",
                    f"- Date planifiee: {draft.scheduled_at.isoformat()}",
                    f"- Statut: {draft.validation_status}",
                    f"- Angle: {draft.angle}",
                    f"- Visuel: {draft.visual_note or 'A definir'}",
                    "",
                    "### Brouillon",
                    "",
                    draft.draft,
                    "",
                ]
            )
        return "\n".join(lines)
