import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # API keys
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    search_api_key: str = field(default_factory=lambda: os.getenv("SEARCH_API_KEY", ""))

    # LLM settings
    model_name: str = "claude-sonnet-4-6"
    max_tokens: int = 2000
    temperature: float = 0.3

    # Agent / loop settings
    max_iterations: int = 3          # hard cap on search->factcheck iterations
    max_sub_questions: int = 6
    max_sources_per_subquestion: int = 5

    # Cache settings
    cache_dir: str = "data/cache"
    cache_ttl_seconds: int = 60 * 60 * 24  # 24 hours

    # Session logging
    sessions_dir: str = "data/research_sessions"

    def validate(self):
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment/.env")