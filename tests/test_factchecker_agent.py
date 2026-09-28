from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.agents.factchecker_agent.claim_extractor import extract_claims
from app.agents.factchecker_agent.factchecker_agent import (
    FactCheckerAgent,
    VerificationResult,
)
from app.config import Config


def test_extract_claims_splits_sentences_and_drops_tiny_fragments():
    text = "Python was created by Guido van Rossum. It is popular. Ok."
    claims = extract_claims(text)
    assert "Python was created by Guido van Rossum." in claims
    assert "Ok." not in claims


@pytest.mark.asyncio
async def test_verify_separates_supported_and_flagged_claims():
    agent = FactCheckerAgent(Config(anthropic_api_key="test-key"))
    agent.llm.complete = AsyncMock(side_effect=["supported", "unsupported"])

    summary = SimpleNamespace(
        text="Python was created by Guido van Rossum. Python is the fastest language ever made."
    )
    sources = [{"url": "https://python.org", "snippet": "Created by Guido van Rossum."}]

    result = await agent.verify(summary, sources)

    assert len(result.verified_claims) == 1
    assert len(result.flagged_claims) == 1
    assert "fastest" in result.flagged_claims[0]


@pytest.mark.asyncio
async def test_contradicted_claims_are_flagged():
    agent = FactCheckerAgent(Config(anthropic_api_key="test-key"))
    agent.llm.complete = AsyncMock(return_value="contradicted")
    summary = SimpleNamespace(text="The moon is made of cheese, according to sources.")

    result = await agent.verify(summary, [{"url": "u", "snippet": "s"}])

    assert result.verified_claims == []
    assert len(result.flagged_claims) == 1


def test_mark_remaining_as_unverified_moves_flagged_claims():
    result = VerificationResult(flagged_claims=["claim A", "claim B"])
    result.mark_remaining_as_unverified()
    assert result.flagged_claims == []
    assert result.unverified_claims == ["claim A", "claim B"]