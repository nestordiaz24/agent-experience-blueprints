"""FastAPI application exposing normalized agent events over SSE."""

from typing import Annotated, cast

from agent_core import AgentProvider, ConversationRequest, FakeReconciliationProvider
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from agent_api.streaming import stream_provider_events


class ChatStreamRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=16_000)]
    conversation_id: Annotated[str | None, Field(max_length=256)] = None
    response_id: Annotated[str | None, Field(max_length=256)] = None

    @field_validator("message")
    @classmethod
    def message_must_contain_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be blank")
        return value


def create_app(provider: AgentProvider | None = None) -> FastAPI:
    application = FastAPI(title="Agent Experience Blueprints API", version="0.1.0")
    application.state.provider = provider or FakeReconciliationProvider()

    @application.get("/healthz", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post("/v1/chat/stream", tags=["chat"])
    async def stream_chat(payload: ChatStreamRequest, request: Request) -> StreamingResponse:
        conversation = ConversationRequest(
            message=payload.message,
            conversation_id=payload.conversation_id,
            response_id=payload.response_id,
        )
        current_provider = cast(AgentProvider, request.app.state.provider)
        return StreamingResponse(
            stream_provider_events(current_provider, conversation, request.is_disconnected),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "X-Accel-Buffering": "no",
            },
        )

    return application


app = create_app()
