import json
from pathlib import Path

from agent_core import (
    CancellationToken,
    ConversationRequest,
    DoneEvent,
    ErrorEvent,
    FakeReconciliationProvider,
    FinalTextEvent,
    StatusEvent,
    StructuredResultEvent,
    TextDeltaEvent,
    event_to_dict,
    event_to_json,
)
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).parents[2] / "schemas" / "agent-event-v1.schema.json"


async def test_fake_provider_emits_ordered_typed_stream() -> None:
    provider = FakeReconciliationProvider()

    events = [
        event
        async for event in provider.stream(
            ConversationRequest(message="Reconcile the sample records"),
            CancellationToken(),
        )
    ]

    assert [event.stage for event in events if isinstance(event, StatusEvent)] == [
        "ingesting",
        "reconciling",
        "reporting",
    ]
    deltas = [event for event in events if isinstance(event, TextDeltaEvent)]
    assert deltas[-1].accumulated_text == "".join(event.delta for event in deltas)
    structured_results = [
        event for event in events if isinstance(event, StructuredResultEvent)
    ]
    assert [event.kind for event in structured_results] == [
        "reconciliation_summary",
        "table",
        "status_summary",
    ]
    assert isinstance(events[-2], FinalTextEvent)
    assert events[-2].text == deltas[-1].accumulated_text
    assert events[-1] == DoneEvent(reason="completed")
    assert sum(isinstance(event, DoneEvent) for event in events) == 1


async def test_fake_provider_honors_preemptive_cancellation() -> None:
    cancellation = CancellationToken()
    cancellation.cancel()

    events = [
        event
        async for event in FakeReconciliationProvider().stream(
            ConversationRequest(message="Reconcile the sample records"),
            cancellation,
        )
    ]

    assert events == [DoneEvent(reason="cancelled")]


async def test_fake_provider_honors_midstream_cancellation() -> None:
    cancellation = CancellationToken()
    events = []

    async for event in FakeReconciliationProvider().stream(
        ConversationRequest(message="Reconcile the sample records"), cancellation
    ):
        events.append(event)
        if isinstance(event, TextDeltaEvent):
            cancellation.cancel()

    assert isinstance(events[-1], DoneEvent)
    assert events[-1].reason == "cancelled"
    assert not any(isinstance(event, FinalTextEvent) for event in events)
    assert sum(isinstance(event, DoneEvent) for event in events) == 1


async def test_fake_provider_emits_user_safe_error_and_terminal_event() -> None:
    events = [
        event
        async for event in FakeReconciliationProvider(failure_stage="reconciling").stream(
            ConversationRequest(
                message="Reconcile the sample records",
                response_id="response-correlation-id",
            ),
            CancellationToken(),
        )
    ]

    errors = [event for event in events if isinstance(event, ErrorEvent)]
    assert errors == [
        ErrorEvent(
            code="synthetic_provider_error",
            message="The synthetic reconciliation could not be completed.",
            retryable=True,
            correlation_id="response-correlation-id",
        )
    ]
    assert events[-1] == DoneEvent(reason="error")
    assert not any(isinstance(event, FinalTextEvent) for event in events)
    assert sum(isinstance(event, DoneEvent) for event in events) == 1

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    validator.validate(event_to_dict(errors[0]))
    validator.validate(event_to_dict(events[-1]))


async def test_all_fake_provider_events_validate_against_transport_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    events = [
        event
        async for event in FakeReconciliationProvider().stream(
            ConversationRequest(message="Reconcile the sample records"),
            CancellationToken(),
        )
    ]

    for event in events:
        payload = event_to_dict(event)
        validator.validate(payload)
        assert json.loads(event_to_json(event)) == payload


def test_conversation_request_rejects_blank_message() -> None:
    try:
        ConversationRequest(message="   ")
    except ValueError as error:
        assert str(error) == "message must not be empty"
    else:
        raise AssertionError("blank messages must be rejected")
