import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Callable, List


class BaseAbortSignal(ABC):
    def __init__(self):
        self._aborted = False
        self._listeners: List[Callable[[], None]] = []
        self._event = asyncio.Event()

    @property
    def aborted(self) -> bool:
        """Return True if the signal has been aborted."""
        return self._aborted

    def add_listener(self, listener: Callable[[], None]) -> None:
        """Add a listener to be called when the signal is aborted."""
        if self._aborted:
            listener()
        else:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[], None]) -> None:
        """Remove a previously added listener."""
        if not self._aborted:
            self._listeners = [li for li in self._listeners if li != listener]

    @abstractmethod
    def abort(self) -> None:
        pass

    @abstractmethod
    def wait_for_abort(self) -> None:
        pass


class AsyncAbortSignal(BaseAbortSignal):
    """An asynchronous signal that can be used to abort an operation.

    Ported from the AbortSignal class in the JavaScript DOM API.
    Unfortunately we have to distinguish between async/sync abort signals
    due to the nature of calling listeners, but the interface is the same.
    """

    def __init__(self):
        super().__init__()
        self._event = asyncio.Event()

    async def abort(self) -> None:
        """Abort the signal."""
        if not self._aborted:
            self._aborted = True
            for listener in self._listeners:
                await listener()
            self._listeners.clear()
            self._event.set()

    async def wait_for_abort(self) -> None:
        """Wait for the signal to be aborted."""
        await self._event.wait()


class SyncAbortSignal(BaseAbortSignal):
    """A synchronous signal that can be used to abort an operation.

    Ported from the AbortSignal class in the JavaScript DOM API.
    Unfortunately we have to distinguish between async/sync abort signals
    due to the nature of calling listeners, but the interface is the same.
    """

    def __init__(self):
        super().__init__()
        self._event = threading.Event()

    def abort(self) -> None:
        """Abort the signal."""
        if not self._aborted:
            self._aborted = True
            for listener in self._listeners:
                listener()
            self._listeners.clear()
            self._event.set()

    def wait_for_abort(self) -> None:
        """Wait for the signal to be aborted."""
        self._event.wait()
