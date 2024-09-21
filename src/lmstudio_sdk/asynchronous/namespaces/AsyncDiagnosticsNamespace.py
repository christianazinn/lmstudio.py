from ...common import BaseDiagnosticsNamespace


class DiagnosticsNamespace(BaseDiagnosticsNamespace):
    async def connect(self) -> None:
        await self._port.connect()

    async def close(self) -> None:
        await self._port.close()
