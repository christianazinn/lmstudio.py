from abc import ABC
from typing import Generic, TypeVar

from ..communications import BaseClientPort


TClientPort = TypeVar("TClientPort", bound=BaseClientPort)


class BaseNamespace(Generic[TClientPort], ABC):
    _port: TClientPort

    def __init__(self, port: TClientPort):
        self._port = port

    def connect(self) -> None:
        return self._port.connect()

    def close(self) -> None:
        return self._port.close()
