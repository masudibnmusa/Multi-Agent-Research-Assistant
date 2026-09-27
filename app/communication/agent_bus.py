import asyncio
from collections import defaultdict


class AgentBus:
    """Simple in-memory pub/sub queue for agent-to-agent messages.

    Note: not safe for concurrent multi-session use as-is — each session
    should get its own AgentBus instance rather than sharing one globally.
    """

    def __init__(self):
        self._queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    async def publish(self, topic: str, message):
        await self._queues[topic].put(message)

    async def consume(self, topic: str):
        return await self._queues[topic].get()