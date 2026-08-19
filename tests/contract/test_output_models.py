import json
from pathlib import Path

import pytest
from agent_core import (
    ReconciliationSummary,
    StatusItem,
    StatusSummary,
    StructuredResultEvent,
    TableColumn,
    TableResult,
    TableRow,
    event_to_dict,
)
from jsonschema import Draft202012Validator, ValidationError

SCHEMA_PATH = Path(__file__).parents[2] / "schemas" / "agent-event-v1.schema.json"


def test_table_result_requires_unique_columns_and_aligned_rows() -> None:
    with pytest.raises(ValueError, match="column keys must be unique"):
        TableResult(
            title="Duplicate columns",
            columns=(TableColumn(key="id", label="ID"), TableColumn(key="id", label="ID")),
            rows=(),
        )

    with pytest.raises(ValueError, match="one cell per column"):
        TableResult(
            title="Misaligned row",
            columns=(
                TableColumn(key="id", label="ID"),
                TableColumn(key="status", label="Status"),
            ),
            rows=(TableRow(cells=("REC-001",)),),
        )


def test_status_summary_requires_items() -> None:
    with pytest.raises(ValueError, match="at least one item"):
        StatusSummary(title="Empty", overall_state="completed", items=())


def test_structured_result_kind_must_match_data() -> None:
    summary = ReconciliationSummary(title="Summary", status="matched", metrics=(), facts=())

    with pytest.raises(ValueError, match="incompatible structured data"):
        StructuredResultEvent(kind="table", schema_version="1.0", data=summary)


def test_transport_schema_rejects_mismatched_kind_and_data() -> None:
    validator = Draft202012Validator(
        json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    )
    payload = {
        "type": "structured_result",
        "kind": "table",
        "schema_version": "1.0",
        "data": {
            "title": "Wrong payload",
            "status": "matched",
            "metrics": [],
            "facts": [],
        },
    }

    with pytest.raises(ValidationError):
        validator.validate(payload)


def test_valid_table_and_status_summary_events() -> None:
    table = TableResult(
        title="Records requiring review",
        columns=(TableColumn(key="record_id", label="Record"),),
        rows=(TableRow(cells=("REC-004",)),),
    )
    status = StatusSummary(
        title="Workflow status",
        overall_state="completed",
        items=(StatusItem(label="Read records", state="completed"),),
    )

    table_event = StructuredResultEvent(kind="table", schema_version="1.0", data=table)
    status_event = StructuredResultEvent(
        kind="status_summary", schema_version="1.0", data=status
    )

    assert event_to_dict(table_event)["data"] == {
        "title": "Records requiring review",
        "columns": [{"key": "record_id", "label": "Record"}],
        "rows": [{"cells": ["REC-004"]}],
        "truncated": False,
    }
    assert event_to_dict(status_event)["data"] == {
        "title": "Workflow status",
        "overall_state": "completed",
        "items": [{"label": "Read records", "state": "completed", "detail": None}],
    }