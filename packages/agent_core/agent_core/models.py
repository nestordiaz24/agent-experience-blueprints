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


@dataclass(frozen=True, slots=True)
class TableColumn:
    key: str
    label: str


@dataclass(frozen=True, slots=True)
class TableRow:
    cells: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TableResult:
    title: str
    columns: tuple[TableColumn, ...]
    rows: tuple[TableRow, ...]
    truncated: bool = False

    def __post_init__(self) -> None:
        if not self.columns:
            raise ValueError("table must contain at least one column")
        column_keys = [column.key for column in self.columns]
        if any(not key.strip() for key in column_keys):
            raise ValueError("table column keys must not be empty")
        if len(column_keys) != len(set(column_keys)):
            raise ValueError("table column keys must be unique")
        if any(len(row.cells) != len(self.columns) for row in self.rows):
            raise ValueError("table rows must contain one cell per column")


@dataclass(frozen=True, slots=True)
class StatusItem:
    label: str
    state: Literal["pending", "in_progress", "completed", "failed"]
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class StatusSummary:
    title: str
    overall_state: Literal["in_progress", "completed", "failed"]
    items: tuple[StatusItem, ...]

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("status summary must contain at least one item")
