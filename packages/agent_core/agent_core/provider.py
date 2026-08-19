"""Provider boundary used by web and Teams delivery adapters."""

from collections.abc import AsyncIterator
from typing import Protocol

from agent_core.cancellation import CancellationToken
from agent_core.events import AgentEvent
from agent_core.models import ConversationRequest


class AgentProvider(Protocol):
    def stream(
        self,
        request: ConversationRequest,
        cancellation: CancellationToken,
    ) -> AsyncIterator[AgentEvent]: ...
