from typing import List, Callable
from threading import Lock
from asyncio import iscoroutinefunction


class BufferedEvent:
    def __init__(self):
        self.subscribers: List[Callable[[], None]] = []
        self.lock = Lock()

    def subscribeOnce(self, callback: Callable[[], None]):
        with self.lock:
            self.subscribers.append(callback)

    # TODO sync async?????????????????????????????????
    async def emit(self):
        print("attempting to emit")
        with self.lock:
            print("lock acquired")
            for subscriber in self.subscribers:
                await subscriber() if iscoroutinefunction(subscriber) else subscriber()
            print("looped")
            self.subscribers.clear()

    @staticmethod
    def create():
        event = BufferedEvent()
        return event, event.emit
