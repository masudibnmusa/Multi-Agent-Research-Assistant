from unittest.mock import AsyncMock

import pytest

from app.agents.search_agent.search_agent import SearchAgent
from app.agents.search_agent.source_ranker import SourceRanker
from app.config import Config


@pytest.fixture
def config(tmp_path):
    return Config(anthropic_api_key="test-key", cache_dir=str(tmp_path))


def test_ranker_prefers_credible_domains(config):
    ranker = SourceRanker(config)
    sources = [
        {"url": "https://random-blog.com/post", "title": "Blog", "relevance": 0.8},
        {"url": "https://nih.gov/article", "title": "NIH", "relevance": 0.8},
    ]
    ranked = ranker.rank(sources)
    assert ranked[0]["url"] == "https://nih.gov/article"


@pytest.mark.asyncio
async def test_search_returns_ranked_results(config):
    agent = SearchAgent(config)
    agent.tool._call_search_api = AsyncMock(return_value=[
        {"url": "https://blog.com/a", "title": "A", "relevance": 0.9},
        {"url": "https://example.edu/b", "title": "B", "relevance": 0.9},
    ])
    results = await agent.search("some question")
    assert len(results) == 2
    assert results[0]["url"] == "https://example.edu/b"
    assert "score" in results[0]


@pytest.mark.asyncio
async def test_search_uses_cache_on_repeat_query(config):
    agent = SearchAgent(config)
    agent.tool._call_search_api = AsyncMock(return_value=[
        {"url": "https://example.org/a", "title": "A", "relevance": 0.5},
    ])
    await agent.search("same question")
    await agent.search("same question")
    assert agent.tool._call_search_api.call_count == 1


@pytest.mark.asyncio
async def test_expired_cache_triggers_new_search(config):
    config.cache_ttl_seconds = -1  # everything is instantly stale
    agent = SearchAgent(config)
    agent.tool._call_search_api = AsyncMock(return_value=[
        {"url": "https://example.org/a", "title": "A", "relevance": 0.5},
    ])
    await agent.search("q")
    await agent.search("q")
    assert agent.tool._call_search_api.call_count == 2