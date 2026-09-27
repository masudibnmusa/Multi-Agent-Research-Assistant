from dataclasses import dataclass

from app.agents.base_agent import BaseAgent
from app.agents.summarizer_agent.dedup import dedup_points
from app.llm.llm_client import LLMClient
from app.llm.prompt_templates import SUMMARIZE_PROMPT


@dataclass
class Summary:
    text: str
    key_points: list[dict]  # each: {"point": str, "source_urls": [str]}


class SummarizerAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.llm = LLMClient(config)

    async def run(self, sub_question: str, sources: list[dict]):
        return await self.summarize(sub_question, sources)

    async def summarize(self, sub_question: str, sources: list[dict]) -> Summary:
        source_text = "\n\n".join(
            f"[{i}] {s['title']} ({s['url']}):\n{s.get('snippet', '')}"
            for i, s in enumerate(sources)
        )
        prompt = SUMMARIZE_PROMPT.format(sub_question=sub_question, sources=source_text)
        raw_text = await self.llm.complete(prompt)

        key_points = self._extract_points(raw_text, sources)
        # Dedup runs on points that already carry source attribution,
        # so we don't lose the citation trail while merging near-duplicates.
        key_points = dedup_points(key_points)

        return Summary(text=raw_text, key_points=key_points)

    def _extract_points(self, text: str, sources: list[dict]) -> list[dict]:
        # Naive line-based split; replace with structured LLM output if needed.
        points = []
        for line in text.split("\n"):
            line = line.strip("- ").strip()
            if line:
                points.append({"point": line, "source_urls": [s["url"] for s in sources]})
        return points