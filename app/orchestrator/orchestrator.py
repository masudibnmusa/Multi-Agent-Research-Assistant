from app.agents.search_agent.search_agent import SearchAgent
from app.agents.summarizer_agent.summarizer_agent import SummarizerAgent
from app.agents.factchecker_agent.factchecker_agent import FactCheckerAgent
from app.orchestrator.task_decomposer import TaskDecomposer
from app.orchestrator.report_compiler import ReportCompiler
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    def __init__(self, config):
        self.config = config
        self.decomposer = TaskDecomposer(config)
        self.search_agent = SearchAgent(config)
        self.summarizer_agent = SummarizerAgent(config)
        self.factchecker_agent = FactCheckerAgent(config)
        self.compiler = ReportCompiler(config)

    async def run(self, query: str):
        sub_questions = await self.decomposer.decompose(query)
        logger.info(f"Decomposed into {len(sub_questions)} sub-questions")

        results = {}
        for sub_q in sub_questions:
            results[sub_q] = await self._research_subquestion(sub_q)

        report = self.compiler.compile(query, results)
        return report

    async def _research_subquestion(self, sub_question: str):
        sources = await self.search_agent.search(sub_question)
        summary = await self.summarizer_agent.summarize(sub_question, sources)

        iteration = 0
        while iteration < self.config.max_iterations:
            check_result = await self.factchecker_agent.verify(summary, sources)

            if not check_result.flagged_claims:
                break  # all claims verified, stop looping

            logger.info(
                f"Iteration {iteration + 1}: {len(check_result.flagged_claims)} "
                f"claims flagged for '{sub_question}', searching for more sources"
            )
            new_sources = await self.search_agent.search(
                sub_question, extra_context=check_result.flagged_claims
            )
            sources = self._merge_sources(sources, new_sources)
            summary = await self.summarizer_agent.summarize(sub_question, sources)
            iteration += 1
        else:
            logger.warning(
                f"Max iterations ({self.config.max_iterations}) reached for "
                f"'{sub_question}'. Remaining flagged claims marked as unverified."
            )
            check_result = await self.factchecker_agent.verify(summary, sources)
            check_result.mark_remaining_as_unverified()

        return {
            "summary": summary,
            "sources": sources,
            "verification": check_result,
        }

    @staticmethod
    def _merge_sources(existing, new):
        seen_urls = {s["url"] for s in existing}
        merged = list(existing)
        for s in new:
            if s["url"] not in seen_urls:
                merged.append(s)
                seen_urls.add(s["url"])
        return merged