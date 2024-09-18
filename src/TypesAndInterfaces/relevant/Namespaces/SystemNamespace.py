from typing import List

from TypesAndInterfaces.relevant.Defaults.ClientPort import ClientPort
from TypesAndInterfaces.relevant.ModelDescriptors.DownloadedModel import DownloadedModel


class SystemNamespace:
    __port: ClientPort

    def __init__(self, port: ClientPort):
        self.__port = port

    async def connect(self) -> None:
        await self.__port.connect()

    async def close(self) -> None:
        await self.__port.close()

    async def list_downloaded_models(self) -> List[DownloadedModel]:
        """
        List all the models that have been downloaded.
        """
        return await self.__port.call_rpc("listDownloadedModels", None)
