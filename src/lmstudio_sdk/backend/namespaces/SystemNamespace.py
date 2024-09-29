from typing import List

from ...dataclasses import DownloadedModel
from ...utils import LiteralOrCoroutine
from .BaseNamespace import BaseNamespace


class SystemNamespace(BaseNamespace):
    def list_downloaded_models(
        self,
    ) -> LiteralOrCoroutine[List[DownloadedModel]]:
        """
        List all the models that have been downloaded.
        """
        return self._port.call_rpc("listDownloadedModels", None, lambda x: x)
