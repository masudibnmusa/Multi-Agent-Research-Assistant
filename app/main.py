import argparse
import asyncio

from app.config import Config
from app.orchestrator.orchestrator import Orchestrator
from app.utils.logger import get_logger

logger = get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Multi-Agent Research Assistant")
    parser.add_argument("--query", type=str, required=True, help="Research question")
    parser.add_argument("--max-iterations", type=int, default=None,
                         help="Override max fact-check/search iterations")
    return parser.parse_args()


async def run(query: str, max_iterations: int | None = None):
    config = Config()
    if max_iterations is not None:
        config.max_iterations = max_iterations

    orchestrator = Orchestrator(config)
    report = await orchestrator.run(query)

    print("\n" + "=" * 80)
    print(report.to_markdown())
    print("=" * 80)
    return report


def main():
    args = parse_args()
    asyncio.run(run(args.query, args.max_iterations))


if __name__ == "__main__":
    main()