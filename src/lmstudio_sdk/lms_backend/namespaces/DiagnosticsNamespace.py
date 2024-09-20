from ...backend_common import BaseDiagnosticsNamespace


class DiagnosticsNamespace(BaseDiagnosticsNamespace):
    def connect(self) -> None:
        self._port.connect()

    def close(self) -> None:
        self._port.close()
