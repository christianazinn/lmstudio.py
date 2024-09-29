from threading import Lock
from typing import Callable, List


class BufferedEvent:
    def __init__(self):
        self.subscribers: List[Callable[[], None]] = []
        self.lock = Lock()

    def subscribeOnce(self, callback: Callable[[], None]):
        with self.lock:
            self.subscribers.append(callback)

    # TODO deasyncify
    async def emit(self):
        with self.lock:
            for subscriber in self.subscribers:
                await subscriber()
            self.subscribers.clear()

    @staticmethod
    def create():
        event = BufferedEvent()
        return event, event.emit
