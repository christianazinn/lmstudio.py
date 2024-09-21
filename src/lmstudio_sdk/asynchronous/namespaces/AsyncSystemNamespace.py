from typing import List

from ...common import BaseSystemNamespace, DownloadedModel


class SystemNamespace(BaseSystemNamespace):
    async def connect(self) -> None:
        await self._port.connect()

    async def close(self) -> None:
        await self._port.close()

    async def list_downloaded_models(self) -> List[DownloadedModel]:
        """
        List all the models that have been downloaded.
        """
        return await self._port.call_rpc("listDownloadedModels", None)  # type: ignore
