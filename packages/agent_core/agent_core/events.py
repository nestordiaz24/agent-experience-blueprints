"""Normalized asynchronous events shared by every provider and channel."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

from agent_core.models import Citation, ReconciliationSummary


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class StatusEvent:
    stage: str
    message: str
    timestamp: datetime = field(default_factory=_utc_now)
    type: Literal["status"] = field(default="status", init=False)


@dataclass(frozen=True, slots=True)
class TextDeltaEvent:
    delta: str
    accumulated_text: str
    type: Literal["text_delta"] = field(default="text_delta", init=False)


@dataclass(frozen=True, slots=True)
class CitationEvent:
    citation: Citation
    type: Literal["citation"] = field(default="citation", init=False)


@dataclass(frozen=True, slots=True)
class StructuredResultEvent:
    kind: Literal["reconciliation_summary"]
    schema_version: Literal["1.0"]
    data: ReconciliationSummary
    type: Literal["structured_result"] = field(default="structured_result", init=False)


@dataclass(frozen=True, slots=True)
class FinalTextEvent:
    text: str
    type: Literal["final_text"] = field(default="final_text", init=False)


@dataclass(frozen=True, slots=True)
class ErrorEvent:
    code: str
    message: str
    retryable: bool
    correlation_id: str
    type: Literal["error"] = field(default="error", init=False)


@dataclass(frozen=True, slots=True)
class DoneEvent:
    reason: Literal["completed", "cancelled", "error"]
    type: Literal["done"] = field(default="done", init=False)


type AgentEvent = (
    StatusEvent
    | TextDeltaEvent
    | CitationEvent
    | StructuredResultEvent
    | FinalTextEvent
    | ErrorEvent
    | DoneEvent
)
