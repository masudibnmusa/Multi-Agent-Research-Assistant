from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agents.factchecker_agent.factchecker_agent import VerificationResult
from app.agents.summarizer_agent.summarizer_agent import Summary
from app.config import Config
from app.orchestrator.orchestrator import Orchestrator


@pytest.fixture
def orchestrator():
    config = Config(anthropic_api_key="test-key", max_iterations=2)
    orch = Orchestrator(config)

    orch.decomposer = MagicMock()
    orch.decomposer.decompose = AsyncMock(return_value=["sub question 1"])

    orch.search_agent = MagicMock()
    orch.search_agent.search = AsyncMock(
        return_value=[{"url": "https://a.com", "title": "A", "snippet": "s"}]
    )

    orch.summarizer_agent = MagicMock()
    orch.summarizer_agent.summarize = AsyncMock(
        return_value=Summary(text="Some summary text here.", key_points=[])
    )

    orch.factchecker_agent = MagicMock()
    return orch


@pytest.mark.asyncio
async def test_no_flagged_claims_stops_after_one_check(orchestrator):
    orchestrator.factchecker_agent.verify = AsyncMock(
        return_value=VerificationResult(verified_claims=["ok"])
    )

    report = await orchestrator.run("query")

    assert orchestrator.factchecker_agent.verify.call_count == 1
    assert orchestrator.search_agent.search.call_count == 1  # no re-search
    assert report.sections[0]["unverified_claims"] == []


@pytest.mark.asyncio
async def test_iteration_cap_is_enforced_and_claims_marked_unverified(orchestrator):
    # Fact-checker ALWAYS flags something -> would loop forever without a cap
    orchestrator.factchecker_agent.verify = AsyncMock(
        side_effect=lambda *a, **k: VerificationResult(flagged_claims=["shaky claim"])
    )

    report = await orchestrator.run("query")

    # max_iterations=2 loop checks + 1 final check after the cap is hit
    assert orchestrator.factchecker_agent.verify.call_count == 3
    assert report.sections[0]["unverified_claims"] == ["shaky claim"]


@pytest.mark.asyncio
async def test_flagged_claims_trigger_additional_search(orchestrator):
    orchestrator.factchecker_agent.verify = AsyncMock(
        side_effect=[
            VerificationResult(flagged_claims=["needs more evidence"]),
            VerificationResult(verified_claims=["needs more evidence"]),
        ]
    )

    await orchestrator.run("query")

    assert orchestrator.search_agent.search.call_count == 2  # initial + follow-up


def test_merge_sources_dedupes_by_url():
    existing = [{"url": "a"}, {"url": "b"}]
    new = [{"url": "b"}, {"url": "c"}]
    merged = Orchestrator._merge_sources(existing, new)
    assert [s["url"] for s in merged] == ["a", "b", "c"]