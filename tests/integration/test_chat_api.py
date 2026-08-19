import json
from collections.abc import AsyncIterator

import httpx
from agent_api import create_app
from agent_api.streaming import stream_provider_events
from agent_core import (
    AgentEvent,
    CancellationToken,
    ConversationRequest,
    DoneEvent,
    StatusEvent,
)


def _parse_sse(content: str) -> list[dict[str, str]]:
    parsed = []
    for block in content.strip().split("\n\n"):
        fields = dict(line.split(": ", maxsplit=1) for line in block.splitlines())
        parsed.append(fields)
    return parsed


async def test_health_endpoint_reports_ready() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        response = await client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_chat_stream_returns_normalized_named_events() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/chat/stream", json={"message": "Reconcile the sample records"}
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["cache-control"] == "no-cache, no-transform"
    assert response.headers["x-accel-buffering"] == "no"
    events = _parse_sse(response.text)
    assert [event["id"] for event in events] == [str(index) for index in range(1, 12)]
    assert [event["event"] for event in events] == [
        "status",
        "status",
        "status",
        "text_delta",
        "text_delta",
        "citation",
        "structured_result",
        "structured_result",
        "structured_result",
        "final_text",
        "done",
    ]
    assert json.loads(events[-1]["data"]) == {"type": "done", "reason": "completed"}


async def test_chat_stream_rejects_blank_messages() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        response = await client.post("/v1/chat/stream", json={"message": "   "})

    assert response.status_code == 422


class ExplodingProvider:
    async def stream(
        self, request: ConversationRequest, cancellation: CancellationToken
    ) -> AsyncIterator[AgentEvent]:
        del request, cancellation
        yield StatusEvent(stage="starting", message="Starting synthetic work")
        raise RuntimeError("provider detail that must not reach the client")


async def test_chat_stream_translates_unexpected_provider_errors() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app(ExplodingProvider())),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/v1/chat/stream",
            json={"message": "Run", "response_id": "safe-correlation-id"},
        )

    events = _parse_sse(response.text)
    assert [event["event"] for event in events] == ["status", "error", "done"]
    error = json.loads(events[-2]["data"])
    assert error == {
        "type": "error",
        "code": "provider_stream_error",
        "message": "The response stream ended unexpectedly.",
        "retryable": True,
        "correlation_id": "safe-correlation-id",
    }
    assert "provider detail" not in response.text


class WaitingProvider:
    cancellation: CancellationToken | None = None

    async def stream(
        self, request: ConversationRequest, cancellation: CancellationToken
    ) -> AsyncIterator[AgentEvent]:
        del request
        self.cancellation = cancellation
        yield StatusEvent(stage="waiting", message="Waiting for cancellation")
        await cancellation.wait()
        yield DoneEvent(reason="cancelled")


async def test_closing_delivery_stream_cancels_provider_work() -> None:
    provider = WaitingProvider()

    async def connected() -> bool:
        return False

    stream = stream_provider_events(
        provider,
        ConversationRequest(message="Start"),
        connected,
    )
    first_event = await anext(stream)
    await stream.aclose()

    assert "event: status" in first_event
    assert provider.cancellation is not None
    assert provider.cancellation.is_cancelled
