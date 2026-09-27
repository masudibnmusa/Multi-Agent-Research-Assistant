from collections import defaultdict


class CitationTracker:
    """Maintains a mapping of claim -> supporting source URLs across the pipeline."""

    def __init__(self):
        self._map: dict[str, set[str]] = defaultdict(set)

    def add(self, claim: str, source_urls: list[str]):
        self._map[claim].update(source_urls)

    def sources_for(self, claim: str) -> list[str]:
        return sorted(self._map.get(claim, []))

    def as_dict(self) -> dict[str, list[str]]:
        return {claim: sorted(urls) for claim, urls in self._map.items()}