import threading
from abc import ABC, abstractmethod
from typing import Callable, List


class BaseBufferedEvent(ABC):
    def __init__(self):
        self.subscribers: List[Callable[[], None]] = []
        self.lock = threading.Lock()

    def subscribeOnce(self, callback: Callable[[], None]):
        with self.lock:
            self.subscribers.append(callback)

    @abstractmethod
    def emit(self):
        pass

    @staticmethod
    @abstractmethod
    def create() -> tuple["BaseBufferedEvent", Callable[[], None]]:
        pass


class AsyncBufferedEvent(BaseBufferedEvent):
    # TODO docstring
    async def emit(self):
        with self.lock:
            for subscriber in self.subscribers:
                await subscriber()
            self.subscribers.clear()

    @staticmethod
    def create() -> tuple["AsyncBufferedEvent", Callable[[], None]]:
        event = AsyncBufferedEvent()
        return event, event.emit


class SyncBufferedEvent(BaseBufferedEvent):
    # TODO docstring
    def emit(self):
        with self.lock:
            for subscriber in self.subscribers:
                subscriber()
            self.subscribers.clear()

    @staticmethod
    def create() -> tuple["SyncBufferedEvent", Callable[[], None]]:
        event = SyncBufferedEvent()
        return event, event.emit
