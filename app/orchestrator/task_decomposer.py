import json

from app.llm.llm_client import LLMClient
from app.llm.prompt_templates import TASK_DECOMPOSITION_PROMPT


class TaskDecomposer:
    def __init__(self, config):
        self.config = config
        self.llm = LLMClient(config)

    async def decompose(self, query: str) -> list[str]:
        prompt = TASK_DECOMPOSITION_PROMPT.format(
            query=query,
            max_sub_questions=self.config.max_sub_questions,
        )
        response = await self.llm.complete(prompt, json_mode=True)

        try:
            data = json.loads(response)
            sub_questions = data.get("sub_questions", [])
        except json.JSONDecodeError:
            sub_questions = [query]  # fallback: treat whole query as one sub-question

        return sub_questions[: self.config.max_sub_questions] or [query]