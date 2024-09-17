from typing import List
from pydantic import TypeAdapter

from TypesAndInterfaces.relevant.Defaults.ClientPort import ClientPort
from TypesAndInterfaces.relevant.ModelDescriptors.DownloadedModel import DownloadedModel


class SystemNamespace:
    port: ClientPort

    async def list_downloaded_models(self) -> List[DownloadedModel]:
        """
        List all the models that have been downloaded.
        """
        # TODO: the list returned is broken in ClientPort call_rpc because of comprotinc
        adapter = TypeAdapter(List[DownloadedModel])
        return adapter.validate_python(await self.port.call_rpc("listDownloadedModels", None))
