from app.agents.base_agent import BaseAgent
from app.agents.search_agent.search_tool import SearchTool
from app.agents.search_agent.source_ranker import SourceRanker


class SearchAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.tool = SearchTool(config)
        self.ranker = SourceRanker(config)

    async def run(self, sub_question: str, extra_context: list[str] | None = None):
        return await self.search(sub_question, extra_context)

    async def search(self, sub_question: str, extra_context: list[str] | None = None):
        query = sub_question
        if extra_context:
            query += " " + " ".join(extra_context)

        raw_results = await self.tool.search(query, max_results=self.config.max_sources_per_subquestion)
        ranked = self.ranker.rank(raw_results)
        return ranked