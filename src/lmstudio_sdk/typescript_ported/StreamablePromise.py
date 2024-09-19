from __future__ import annotations
from typing import Generic, TypeVar, List, Optional, AsyncIterator, Any
import asyncio
from abc import ABC, abstractmethod


TFragment = TypeVar("TFragment")
TFinal = TypeVar("TFinal")


class StreamablePromise(Generic[TFragment, TFinal], ABC):
    def __init__(self):
        self.queue: asyncio.Queue[Optional[TFragment]] = asyncio.Queue()
        self.promise_final: asyncio.Future[TFinal] = asyncio.Future()
        self.status: str = "pending"
        self.buffer: List[TFragment] = []

    @abstractmethod
    async def collect(self, fragments: List[TFragment]) -> TFinal:
        pass

    def push(self, fragment: TFragment) -> None:
        if self.status != "pending":
            return
        self.buffer.append(fragment)
        self.queue.put_nowait(fragment)

    def finished(self, error: Optional[Any] = None) -> None:
        if self.status != "pending":
            return

        if error:
            self.status = "rejected"
            self.promise_final.set_exception(error)
        else:
            self.status = "resolved"
            asyncio.create_task(self._resolve())

        self.queue.put_nowait(None)  # Signal end of stream

    async def _resolve(self):
        try:
            result = await self.collect(self.buffer)
            self.promise_final.set_result(result)
        except Exception as e:
            self.promise_final.set_exception(e)

    def __await__(self):
        return self.promise_final.__await__()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __aiter__(self) -> AsyncIterator[TFragment]:
        return self

    async def __anext__(self) -> TFragment:
        item = await self.queue.get()
        if item is None:
            if self.status == "rejected":
                raise Exception()
            raise StopAsyncIteration
        return item
