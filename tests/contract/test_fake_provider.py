from agent_core import (
    CancellationToken,
    ConversationRequest,
    DoneEvent,
    FakeReconciliationProvider,
    FinalTextEvent,
    StatusEvent,
    StructuredResultEvent,
    TextDeltaEvent,
)


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
    assert isinstance(events[-3], StructuredResultEvent)
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


def test_conversation_request_rejects_blank_message() -> None:
    try:
        ConversationRequest(message="   ")
    except ValueError as error:
        assert str(error) == "message must not be empty"
    else:
        raise AssertionError("blank messages must be rejected")
