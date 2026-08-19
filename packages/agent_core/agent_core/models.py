"""Typed requests and channel-independent structured outputs."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class ConversationRequest:
    message: str
    conversation_id: str | None = None
    response_id: str | None = None

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("message must not be empty")


@dataclass(frozen=True, slots=True)
class Citation:
    title: str
    url: str
    source_type: Literal["synthetic", "web", "work"]


@dataclass(frozen=True, slots=True)
class Metric:
    label: str
    value: str
    trend: Literal["up", "down", "neutral"] = "neutral"


@dataclass(frozen=True, slots=True)
class Fact:
    label: str
    value: str


@dataclass(frozen=True, slots=True)
class ReconciliationSummary:
    title: str
    status: Literal["matched", "review_required", "failed"]
    metrics: tuple[Metric, ...]
    facts: tuple[Fact, ...]
