from __future__ import annotations

import json
from pathlib import Path

from .models import XSample


class XSampleSource:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[XSample]:
        if not self.path.exists():
            raise FileNotFoundError(f"X samples file not found: {self.path}")

        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [XSample.model_validate(item) for item in payload]
