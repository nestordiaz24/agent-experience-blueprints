"""JSON transport serialization for normalized agent events."""

import json
from datetime import UTC
from typing import assert_never

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
from agent_core.models import Citation, ReconciliationSummary, StatusSummary, TableResult

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


def event_to_dict(event: AgentEvent) -> JsonObject:
    """Convert one normalized event to its versioned JSON-compatible shape."""

    if isinstance(event, StatusEvent):
        return {
            "type": event.type,
            "stage": event.stage,
            "message": event.message,
            "timestamp": event.timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        }
    if isinstance(event, TextDeltaEvent):
        return {
            "type": event.type,
            "delta": event.delta,
            "accumulated_text": event.accumulated_text,
        }
    if isinstance(event, CitationEvent):
        return {"type": event.type, "citation": _citation_to_dict(event.citation)}
    if isinstance(event, StructuredResultEvent):
        return {
            "type": event.type,
            "kind": event.kind,
            "schema_version": event.schema_version,
            "data": _structured_result_to_dict(event.data),
        }
    if isinstance(event, FinalTextEvent):
        return {"type": event.type, "text": event.text}
    if isinstance(event, ErrorEvent):
        return {
            "type": event.type,
            "code": event.code,
            "message": event.message,
            "retryable": event.retryable,
            "correlation_id": event.correlation_id,
        }
    if isinstance(event, DoneEvent):
        return {"type": event.type, "reason": event.reason}
    assert_never(event)


def event_to_json(event: AgentEvent) -> str:
    """Serialize one normalized event without provider-specific objects."""

    return json.dumps(event_to_dict(event), separators=(",", ":"), ensure_ascii=True)


def _citation_to_dict(citation: Citation) -> JsonObject:
    return {
        "title": citation.title,
        "url": citation.url,
        "source_type": citation.source_type,
    }


def _summary_to_dict(summary: ReconciliationSummary) -> JsonObject:
    return {
        "title": summary.title,
        "status": summary.status,
        "metrics": [
            {"label": metric.label, "value": metric.value, "trend": metric.trend}
            for metric in summary.metrics
        ],
        "facts": [{"label": fact.label, "value": fact.value} for fact in summary.facts],
    }


def _structured_result_to_dict(
    result: ReconciliationSummary | TableResult | StatusSummary,
) -> JsonObject:
    if isinstance(result, ReconciliationSummary):
        return _summary_to_dict(result)
    if isinstance(result, TableResult):
        return {
            "title": result.title,
            "columns": [
                {"key": column.key, "label": column.label} for column in result.columns
            ],
            "rows": [{"cells": list(row.cells)} for row in result.rows],
            "truncated": result.truncated,
        }
    if isinstance(result, StatusSummary):
        return {
            "title": result.title,
            "overall_state": result.overall_state,
            "items": [
                {
                    "label": item.label,
                    "state": item.state,
                    "detail": item.detail,
                }
                for item in result.items
            ],
        }
    assert_never(result)
