from typing import List

import lmstudio_sdk.dataclasses as dc
import lmstudio_sdk.utils as utils

from .BaseNamespace import BaseNamespace


logger = utils.get_logger(__name__)


class SystemNamespace(BaseNamespace):
    """Method namespace for LM Studio system functions."""

    def list_downloaded_models(
        self,
    ) -> utils.LiteralOrCoroutine[List[dc.DownloadedModel]]:
        """List all the models that have been downloaded."""

        def process_downloaded_models(downloaded_models):
            try:
                return [
                    dc.DownloadedModel(**model) for model in downloaded_models
                ]
            except Exception as e:
                logger.error("Failed to process downloaded models: %s", e)
                return downloaded_models

        return self._port.call_rpc(
            "listDownloadedModels", None, process_downloaded_models
        )
