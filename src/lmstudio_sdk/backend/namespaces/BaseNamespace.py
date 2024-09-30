from abc import ABC

import lmstudio_sdk.backend.communications as comms


class BaseNamespace(ABC):
    _port: comms.BaseClientPort

    def __init__(self, port: comms.BaseClientPort):
        self._port = port

    def connect(self) -> None:
        return self._port.connect()

    def close(self) -> None:
        return self._port.close()
