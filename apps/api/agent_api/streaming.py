"""Server-Sent Event framing and provider stream lifecycle management."""

import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable
from uuid import uuid4

from agent_core import (
    AgentProvider,
    CancellationToken,
    ConversationRequest,
    DoneEvent,
    ErrorEvent,
    event_to_json,
)

type DisconnectCheck = Callable[[], Awaitable[bool]]


async def stream_provider_events(
    provider: AgentProvider,
    conversation: ConversationRequest,
    is_disconnected: DisconnectCheck,
) -> AsyncGenerator[str]:
    """Frame provider events as SSE and cancel work when delivery ends."""

    cancellation = CancellationToken()
    sequence = 0
    try:
        async for event in provider.stream(conversation, cancellation):
            if await is_disconnected():
                return
            sequence += 1
            yield _encode_sse(sequence, event.type, event_to_json(event))
    except asyncio.CancelledError:
        raise
    except Exception:
        if not await is_disconnected():
            correlation_id = (
                conversation.response_id or conversation.conversation_id or str(uuid4())
            )
            error = ErrorEvent(
                code="provider_stream_error",
                message="The response stream ended unexpectedly.",
                retryable=True,
                correlation_id=correlation_id,
            )
            sequence += 1
            yield _encode_sse(sequence, error.type, event_to_json(error))
            done = DoneEvent(reason="error")
            sequence += 1
            yield _encode_sse(sequence, done.type, event_to_json(done))
    finally:
        cancellation.cancel()


def _encode_sse(sequence: int, event_type: str, data: str) -> str:
    return f"id: {sequence}\nevent: {event_type}\ndata: {data}\n\n"
