from dataclasses import dataclass, field

from app.agents.base_agent import BaseAgent
from app.agents.factchecker_agent.claim_extractor import extract_claims
from app.llm.llm_client import LLMClient
from app.llm.prompt_templates import FACTCHECK_PROMPT


@dataclass
class VerificationResult:
    verified_claims: list[str] = field(default_factory=list)
    flagged_claims: list[str] = field(default_factory=list)
    unverified_claims: list[str] = field(default_factory=list)

    def mark_remaining_as_unverified(self):
        self.unverified_claims.extend(self.flagged_claims)
        self.flagged_claims = []


class FactCheckerAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.llm = LLMClient(config)

    async def run(self, summary, sources):
        return await self.verify(summary, sources)

    async def verify(self, summary, sources: list[dict]) -> VerificationResult:
        claims = extract_claims(summary.text)
        source_text = "\n\n".join(f"({s['url']}): {s.get('snippet', '')}" for s in sources)

        result = VerificationResult()
        for claim in claims:
            prompt = FACTCHECK_PROMPT.format(claim=claim, sources=source_text)
            verdict = (await self.llm.complete(prompt)).strip().lower()

            if verdict.startswith("supported"):
                result.verified_claims.append(claim)
            else:
                result.flagged_claims.append(claim)

        return result