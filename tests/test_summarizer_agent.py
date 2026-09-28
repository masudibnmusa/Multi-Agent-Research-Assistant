from unittest.mock import AsyncMock

import pytest

from app.agents.summarizer_agent.dedup import dedup_points
from app.agents.summarizer_agent.summarizer_agent import SummarizerAgent
from app.config import Config


def test_dedup_merges_near_duplicates_and_keeps_all_sources():
    points = [
        {"point": "Water boils at 100 degrees Celsius.", "source_urls": ["a.com"]},
        {"point": "Water boils at 100 degrees Celsius", "source_urls": ["b.com"]},
        {"point": "Ice melts at 0 degrees Celsius.", "source_urls": ["c.com"]},
    ]
    result = dedup_points(points)
    assert len(result) == 2
    merged = next(p for p in result if "boils" in p["point"])
    assert set(merged["source_urls"]) == {"a.com", "b.com"}


@pytest.mark.asyncio
async def test_summarize_builds_summary_with_key_points():
    agent = SummarizerAgent(Config(anthropic_api_key="test-key"))
    agent.llm.complete = AsyncMock(
        return_value="- Point one is here.\n- Point two is here."
    )
    sources = [{"url": "https://x.com", "title": "X", "snippet": "text"}]

    summary = await agent.summarize("What is X?", sources)

    assert "Point one" in summary.text
    assert len(summary.key_points) == 2
    assert summary.key_points[0]["source_urls"] == ["https://x.com"]