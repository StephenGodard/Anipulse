from __future__ import annotations

from .animesphere import AnimeSphereClient
from .models import TrendCandidate, XSample


FAN_SIGNAL_WORDS = (
    "banger",
    "masterclass",
    "peak",
    "dinguerie",
    "choque",
    "hype",
    "gooooo",
    "meilleur episode",
)


class TrendAnalyzer:
    def __init__(self, animesphere: AnimeSphereClient) -> None:
        self.animesphere = animesphere

    def analyze(self, samples: list[XSample]) -> list[TrendCandidate]:
        candidates: list[TrendCandidate] = []
        for sample in samples:
            for title in sample.candidate_titles:
                anime = self.animesphere.search_first(title)
                if not anime:
                    continue

                score, reasons = self._score(sample)
                candidates.append(
                    TrendCandidate(
                        sample=sample,
                        anime=anime,
                        score=score,
                        reasons=reasons,
                    )
                )

        return sorted(candidates, key=lambda item: item.score, reverse=True)

    def _score(self, sample: XSample) -> tuple[float, list[str]]:
        score = 10.0
        reasons = ["anime present sur AnimeSphere"]

        engagement = (
            sample.metrics.likes * 1.0
            + sample.metrics.reposts * 2.0
            + sample.metrics.replies * 1.5
            + sample.metrics.views * 0.01
        )
        score += min(engagement / 50, 30)
        reasons.append("engagement X detecte")

        if sample.media_count:
            score += min(sample.media_count * 3, 12)
            reasons.append("post avec visuels")

        text = sample.text.lower()
        signal_hits = [word for word in FAN_SIGNAL_WORDS if word in text]
        if signal_hits:
            score += len(signal_hits) * 5
            reasons.append(f"ton fan/react: {', '.join(signal_hits)}")

        return score, reasons
