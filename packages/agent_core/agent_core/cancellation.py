"""Cooperative cancellation primitives for provider streams."""

import asyncio


class CancellationToken:
    """Signals that an active provider stream should stop producing work."""

    def __init__(self) -> None:
        self._cancelled = asyncio.Event()

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled.is_set()

    def cancel(self) -> None:
        self._cancelled.set()

    async def wait(self) -> None:
        await self._cancelled.wait()
