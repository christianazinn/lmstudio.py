from typing import List

from ...dataclasses import DownloadedModel
from ...utils import sync_async_decorator
from ..communications import BaseClientPort


class SystemNamespace:
    _port: BaseClientPort

    def __init__(self, port: BaseClientPort):
        self._port = port

    @sync_async_decorator(obj_method="connect", process_result=lambda x: None)
    def connect(self) -> None:
        return {}

    @sync_async_decorator(obj_method="close", process_result=lambda x: None)
    def close(self) -> None:
        return {}

    def list_downloaded_models(self) -> List[DownloadedModel]:
        """
        List all the models that have been downloaded.
        """
        return self._port.call_rpc("listDownloadedModels", None, lambda x: x)
