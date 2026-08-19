"""Deterministic synthetic provider for local development and contract tests."""

from collections.abc import AsyncIterator, Iterable
from typing import Literal

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

type FailureStage = Literal["ingesting", "reconciling", "reporting"]


class FakeReconciliationProvider:
    """Emits a stable record-reconciliation workflow without cloud credentials."""

    def __init__(self, failure_stage: FailureStage | None = None) -> None:
        self._failure_stage = failure_stage

    async def stream(
        self,
        request: ConversationRequest,
        cancellation: CancellationToken,
    ) -> AsyncIterator[AgentEvent]:
        for stage, message in (
            ("ingesting", "Reading synthetic records"),
            ("reconciling", "Comparing record identifiers and amounts"),
            ("reporting", "Preparing the reconciliation summary"),
        ):
            if cancellation.is_cancelled:
                yield DoneEvent(reason="cancelled")
                return
            yield StatusEvent(stage=stage, message=message)
            if stage == self._failure_stage:
                yield ErrorEvent(
                    code="synthetic_provider_error",
                    message="The synthetic reconciliation could not be completed.",
                    retryable=True,
                    correlation_id=(
                        request.response_id or request.conversation_id or "fake-correlation-id"
                    ),
                )
                yield DoneEvent(reason="error")
                return

        summary = ReconciliationSummary(
            title="Synthetic record reconciliation",
            status="review_required",
            metrics=(
                Metric(label="Records checked", value="12"),
                Metric(label="Matched", value="10"),
                Metric(label="Needs review", value="2"),
            ),
            facts=(Fact(label="Data source", value="Generated sample records"),),
        )
        answer_chunks = (
            "The synthetic reconciliation checked 12 records. ",
            "Ten matched automatically, and two need review.",
        )
        accumulated_text = ""
        for chunk in self._until_cancelled(answer_chunks, cancellation):
            accumulated_text += chunk
            yield TextDeltaEvent(delta=chunk, accumulated_text=accumulated_text)

        if cancellation.is_cancelled:
            yield DoneEvent(reason="cancelled")
            return

        yield CitationEvent(
            citation=Citation(
                title="Synthetic reconciliation fixture",
                url="https://example.com/reconciliation-fixture",
                source_type="synthetic",
            )
        )
        yield StructuredResultEvent(
            kind="reconciliation_summary",
            schema_version="1.0",
            data=summary,
        )
        yield StructuredResultEvent(
            kind="table",
            schema_version="1.0",
            data=TableResult(
                title="Records requiring review",
                columns=(
                    TableColumn(key="record_id", label="Record"),
                    TableColumn(key="issue", label="Issue"),
                ),
                rows=(
                    TableRow(cells=("SYN-004", "Amount differs")),
                    TableRow(cells=("SYN-009", "Identifier missing")),
                ),
            ),
        )
        yield StructuredResultEvent(
            kind="status_summary",
            schema_version="1.0",
            data=StatusSummary(
                title="Reconciliation workflow",
                overall_state="completed",
                items=(
                    StatusItem(label="Read records", state="completed"),
                    StatusItem(label="Compare records", state="completed"),
                    StatusItem(
                        label="Prepare summary",
                        state="completed",
                        detail="Two records require review.",
                    ),
                ),
            ),
        )
        yield FinalTextEvent(text=accumulated_text)
        yield DoneEvent(reason="completed")

    @staticmethod
    def _until_cancelled(
        chunks: Iterable[str], cancellation: CancellationToken
    ) -> Iterable[str]:
        for chunk in chunks:
            if cancellation.is_cancelled:
                return
            yield chunk
