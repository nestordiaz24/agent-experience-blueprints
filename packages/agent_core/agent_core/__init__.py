"""Shared contracts for provider-neutral agent experiences."""

from agent_core.cancellation import CancellationToken
from agent_core.events import (
    AgentEvent,
    CitationEvent,
    DoneEvent,
    ErrorEvent,
    FinalTextEvent,
    StatusEvent,
    StructuredResultEvent,
    TextDeltaEvent,
)
from agent_core.fake_provider import FakeReconciliationProvider
from agent_core.models import (
    Citation,
    ConversationRequest,
    Fact,
    Metric,
    ReconciliationSummary,
    StatusItem,
    StatusSummary,
    TableColumn,
    TableResult,
    TableRow,
)
from agent_core.provider import AgentProvider
from agent_core.serialization import event_to_dict, event_to_json

__all__ = [
    "AgentEvent",
    "AgentProvider",
    "CancellationToken",
    "Citation",
    "CitationEvent",
    "ConversationRequest",
    "DoneEvent",
    "ErrorEvent",
    "Fact",
    "FakeReconciliationProvider",
    "FinalTextEvent",
    "Metric",
    "ReconciliationSummary",
    "StatusEvent",
    "StatusItem",
    "StatusSummary",
    "StructuredResultEvent",
    "TableColumn",
    "TableResult",
    "TableRow",
    "TextDeltaEvent",
    "event_to_dict",
    "event_to_json",
]
