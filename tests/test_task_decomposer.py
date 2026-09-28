import json
from unittest.mock import AsyncMock

import pytest

from app.config import Config
from app.orchestrator.task_decomposer import TaskDecomposer


@pytest.fixture
def decomposer():
    return TaskDecomposer(Config(anthropic_api_key="test-key"))


@pytest.mark.asyncio
async def test_decompose_returns_sub_questions(decomposer):
    decomposer.llm.complete = AsyncMock(
        return_value=json.dumps({"sub_questions": ["What is X?", "Why does X matter?"]})
    )
    result = await decomposer.decompose("Tell me about X")
    assert result == ["What is X?", "Why does X matter?"]


@pytest.mark.asyncio
async def test_decompose_falls_back_on_invalid_json(decomposer):
    decomposer.llm.complete = AsyncMock(return_value="not json at all")
    result = await decomposer.decompose("Tell me about X")
    assert result == ["Tell me about X"]


@pytest.mark.asyncio
async def test_decompose_respects_max_sub_questions(decomposer):
    decomposer.config.max_sub_questions = 2
    decomposer.llm.complete = AsyncMock(
        return_value=json.dumps({"sub_questions": ["a?", "b?", "c?", "d?"]})
    )
    result = await decomposer.decompose("big question")
    assert len(result) == 2


@pytest.mark.asyncio
async def test_decompose_empty_list_falls_back_to_query(decomposer):
    decomposer.llm.complete = AsyncMock(return_value=json.dumps({"sub_questions": []}))
    result = await decomposer.decompose("original query")
    assert result == ["original query"]