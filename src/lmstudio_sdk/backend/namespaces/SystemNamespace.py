from typing import List

import lmstudio_sdk.dataclasses as dc
import lmstudio_sdk.utils as utils

from .BaseNamespace import BaseNamespace


class SystemNamespace(BaseNamespace):
    """Method namespace for LM Studio system functions."""

    def list_downloaded_models(
        self,
    ) -> utils.LiteralOrCoroutine[List[dc.DownloadedModel]]:
        """List all the models that have been downloaded."""
        return self._port.call_rpc("listDownloadedModels", None, lambda x: x)
