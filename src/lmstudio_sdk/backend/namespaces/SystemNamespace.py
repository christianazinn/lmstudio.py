from typing import List

from ...dataclasses import DownloadedModel
from ..communications import BaseClientPort


class SystemNamespace:
    _port: BaseClientPort

    def __init__(self, port: BaseClientPort):
        self._port = port

    def connect(self) -> None:
        return self._port.connect()

    def close(self) -> None:
        return self._port.close()

    def list_downloaded_models(self) -> List[DownloadedModel]:
        """
        List all the models that have been downloaded.
        """
        return self._port.call_rpc("listDownloadedModels", None, lambda x: x)
