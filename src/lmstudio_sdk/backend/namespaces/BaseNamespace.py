from abc import ABC

from ..communications import BaseClientPort


class BaseNamespace(ABC):
    _port: BaseClientPort

    def __init__(self, port: BaseClientPort):
        self._port = port

    def connect(self) -> None:
        return self._port.connect()

    def close(self) -> None:
        return self._port.close()
