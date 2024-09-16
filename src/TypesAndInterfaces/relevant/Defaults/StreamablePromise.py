from __future__ import annotations
from typing import Generic, TypeVar, List, Callable, Optional, AsyncIterator, Any
from dataclasses import dataclass
import asyncio
from abc import ABC, abstractmethod

TFragment = TypeVar("TFragment")
TFinal = TypeVar("TFinal")


@dataclass
class NextFragmentPromiseBundle:
    resolve: Callable[[TFragment], None]
    reject: Callable[[Any], None]
    promise: asyncio.Future[TFragment]


class StreamablePromise(Generic[TFragment, TFinal], ABC):
    """
    A StreamablePromise is a promise-like that is also async iterable. This means you can use it as a
    promise (awaiting it, using `.then`, `.catch`, etc.), and you can also use it as an async
    iterable (using `async for`).

    Notably, as much as it implements the async iterable interface, it is not a traditional iterable,
    as it internally maintains a buffer and new values are pushed into the buffer by the producer, as
    opposed to being pulled by the consumer.

    The async iterable interface is used instead of the Node.js object stream because streams are too
    clunky to use, and the `async for` syntax is much more ergonomic for most people.

    If any iterator is created for this instance, an empty rejection handler will be attached to the
    promise to prevent unhandled exception warnings.

    This class is provided as an abstract class and is meant to be extended. Crucially, the `collect`
    method must be implemented, which will be called to convert a list of values into the final
    resolved value of the promise.

    In addition, the constructor of the subclass should be marked as private, and a static method
    that exposes the constructor, the `finished` method, and the `push` method should be provided.

    Args:
        TFragment: The type of the individual fragments that are pushed into the buffer.
        TFinal: The type of the final resolved value of the promise.
    """

    def __init__(self):
        self.promise_final: asyncio.Future[TFinal] = asyncio.Future()
        self.status: str = "pending"
        self.buffer: List[TFragment] = []
        self.next_fragment_promise_bundle: Optional[NextFragmentPromiseBundle] = None
        self.has_iterator: bool = False

    @abstractmethod
    async def collect(self, fragments: List[TFragment]) -> TFinal:
        """
        Convert an array of fragments into the final resolved value of the promise.
        This method must be implemented by subclasses.
        """
        pass

    def finished(self, error: Optional[Any] = None) -> None:
        """
        Called by the producer when it has finished producing values. If an error is provided, the
        promise will be rejected with that error. If no error is provided, the promise will be resolved
        with the final value.

        This method should be exposed in the static constructor of the subclass.

        Args:
            error: The error to reject the promise with, if any.
        """
        if self.status != "pending":
            return

        if error:
            self.status = "rejected"
            self.promise_final.set_exception(error)
            if self.next_fragment_promise_bundle:
                self.next_fragment_promise_bundle.reject(error)
        else:
            self.status = "resolved"
            asyncio.create_task(self._resolve())

    async def _resolve(self):
        try:
            result = await self.collect(self.buffer)
            self.promise_final.set_result(result)
        except Exception as e:
            self.promise_final.set_exception(e)

    def push(self, fragment: TFragment) -> None:
        """
        Called by the producer to push a new fragment into the buffer. This method should be exposed in
        the static constructor of the subclass.

        Args:
            fragment: The fragment to push into the buffer.
        """
        if self.status != "pending":
            return

        self.buffer.append(fragment)
        if self.next_fragment_promise_bundle:
            self.next_fragment_promise_bundle.resolve(fragment)
            self.next_fragment_promise_bundle = None

    def __await__(self):
        return self.promise_final.__await__()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __aiter__(self) -> AsyncIterator[TFragment]:
        if not self.has_iterator:
            self.has_iterator = True
            self.promise_final.add_done_callback(lambda _: None)  # Prevent unhandled exception warnings
        return self

    async def __anext__(self) -> TFragment:
        if self.buffer:
            return self.buffer.pop(0)
        if self.status == "resolved":
            raise StopAsyncIteration
        if self.status == "rejected":
            raise self.promise_final.exception()
        bundle = self._obtain_next_fragment_promise_bundle()
        try:
            return await bundle.promise
        except Exception:
            if self.status == "rejected":
                raise self.promise_final.exception()
            raise

    def _obtain_next_fragment_promise_bundle(self) -> NextFragmentPromiseBundle:
        if self.next_fragment_promise_bundle:
            return self.next_fragment_promise_bundle
        promise = asyncio.Future()
        bundle = NextFragmentPromiseBundle(resolve=promise.set_result, reject=promise.set_exception, promise=promise)
        self.next_fragment_promise_bundle = bundle
        return bundle
