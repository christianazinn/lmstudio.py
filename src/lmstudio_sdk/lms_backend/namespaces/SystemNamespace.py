from typing import List

from ...lms_dataclasses import DownloadedModel
from ..communications import ClientPort


class SystemNamespace:
    __port: ClientPort

    def __init__(self, port: ClientPort):
        self.__port = port

    def connect(self) -> None:
        self.__port.connect()

    def close(self) -> None:
        self.__port.close()

    def list_downloaded_models(self) -> List[DownloadedModel]:
        """
        List all the models that have been downloaded.
        """
        return self.__port.call_rpc("listDownloadedModels", None)  # type: ignore
