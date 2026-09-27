import anthropic


class LLMClient:
    def __init__(self, config):
        self.config = config
        self.client = anthropic.AsyncAnthropic(api_key=config.anthropic_api_key)

    async def complete(self, prompt: str, json_mode: bool = False) -> str:
        system = "Respond only with valid JSON, no preamble or markdown." if json_mode else None

        response = await self.client.messages.create(
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")