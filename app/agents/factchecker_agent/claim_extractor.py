import re

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def extract_claims(summary_text: str) -> list[str]:
    """Split summary text into discrete, checkable claims (one per sentence)."""
    sentences = SENTENCE_SPLIT_RE.split(summary_text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]