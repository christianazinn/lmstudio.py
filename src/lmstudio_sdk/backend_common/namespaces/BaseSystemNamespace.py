from ..communications import BaseClientPort


class BaseSystemNamespace:
    _port: BaseClientPort

    def __init__(self, port: BaseClientPort):
        self._port = port
