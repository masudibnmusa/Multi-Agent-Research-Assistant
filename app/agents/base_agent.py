from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Shared interface all agents implement."""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    async def run(self, *args, **kwargs):
        """Execute the agent's core task. Each agent defines its own signature
        via a more specific public method (e.g. search(), summarize(), verify())
        that internally calls this."""
        raise NotImplementedError