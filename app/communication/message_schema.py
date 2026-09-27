from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    SEARCH_REQUEST = "search_request"
    SEARCH_RESULT = "search_result"
    SUMMARY_REQUEST = "summary_request"
    SUMMARY_RESULT = "summary_result"
    FACTCHECK_REQUEST = "factcheck_request"
    FACTCHECK_RESULT = "factcheck_result"


@dataclass
class AgentMessage:
    type: MessageType
    sender: str
    payload: dict
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())