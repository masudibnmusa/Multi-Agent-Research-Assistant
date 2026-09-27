from urllib.parse import urlparse

# Simple starter credibility weights — expand as needed
DOMAIN_WEIGHTS = {
    ".gov": 1.0,
    ".edu": 0.9,
    ".org": 0.6,
    "wikipedia.org": 0.5,
}
DEFAULT_WEIGHT = 0.4


class SourceRanker:
    def __init__(self, config):
        self.config = config

    def rank(self, sources: list[dict]) -> list[dict]:
        scored = [
            {**src, "score": self._score(src)}
            for src in sources
        ]
        return sorted(scored, key=lambda s: s["score"], reverse=True)

    def _score(self, source: dict) -> float:
        relevance = source.get("relevance", 0.5)  # from search API, 0-1
        credibility = self._credibility(source.get("url", ""))
        return 0.6 * relevance + 0.4 * credibility

    def _credibility(self, url: str) -> float:
        domain = urlparse(url).netloc.lower()
        for pattern, weight in DOMAIN_WEIGHTS.items():
            if pattern in domain:
                return weight
        return DEFAULT_WEIGHT