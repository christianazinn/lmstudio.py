from typing import List

from ...lms_dataclasses import DownloadedModel
from ...backend_common import BaseSystemNamespace


class SystemNamespace(BaseSystemNamespace):
    def connect(self) -> None:
        self._port.connect()

    def close(self) -> None:
        self._port.close()

    def list_downloaded_models(self) -> List[DownloadedModel]:
        """
        List all the models that have been downloaded.
        """
        return self._port.call_rpc("listDownloadedModels", None)  # type: ignore
