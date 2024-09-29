from abc import ABC, abstractmethod
from urllib.parse import urlparse

from ...utils import generate_random_base64, get_logger
from ..namespaces import DiagnosticsNamespace, EmbeddingNamespace, LLMNamespace, SystemNamespace


logger = get_logger(__name__)


class LMStudioClient(ABC):
    client_identifier: str
    base_url: str | None

    llm: LLMNamespace = None
    embedding: EmbeddingNamespace = None
    system: SystemNamespace = None
    diagnostics: DiagnosticsNamespace = None

    def _validate_base_url_or_throw(self, base_url):
        error_msg = None
        try:
            url = urlparse(base_url)
        except ValueError:
            error_msg = f"Failed to construct LMStudioClient. The baseUrl passed in is invalid. Received: {base_url}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if url.scheme not in ["ws", "wss"]:
            error_msg = f"""
                    Failed to construct LMStudioClient. The baseUrl passed in must have protocol "ws" or "wss". \
                    Received: {base_url}
                """

        elif url.query:
            error_msg = f"""
                    Failed to construct LMStudioClient. The baseUrl passed contains search parameters \
                    ("{url.query}").
                """

        elif url.fragment:
            error_msg = f"Failed to construct LMStudioClient. The baseUrl passed contains a hash ('{url.fragment}')."

        elif url.username or url.password:
            error_msg = f"""
                    Failed to construct LMStudioClient. The baseUrl passed contains a username or password. We \
                    do not support these in the baseUrl. Received: {base_url}
                """

        elif base_url.endswith("/"):
            error_msg = f"""
                    Failed to construct LMStudioClient. The baseUrl passed in must not end with a "/". If you \
                    are reverse-proxying, you should remove the trailing slash from the baseUrl. Received: \
                    {base_url}
                """

        if error_msg:
            logger.error(error_msg)
            raise ValueError(error_msg)

    @abstractmethod
    def _is_localhost_with_given_port_lmstudio_server(self, port: int) -> int:
        pass

    @abstractmethod
    def _guess_base_url(self) -> str:
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    def _create_ports(self, is_async: bool):
        error_msg = None
        if self.base_url is None:
            error_msg = "Failed to create ports: base_url is None"
        elif self.client_identifier is None:
            error_msg = "Failed to create ports: client_identifier is None"
        elif self.__client_passkey is None:
            error_msg = "Failed to create ports: client_passkey is None"

        if error_msg:
            logger.error(error_msg)
            raise ValueError(error_msg)

        if is_async:
            from ..communications import AsyncClientPort as ClientPort
        else:
            from ..communications import SyncClientPort as ClientPort
        logger.info(
            f"Creating {'async' if is_async else 'sync'} ports at {self.base_url} as {self.client_identifier}..."
        )

        llm_port = ClientPort(self.base_url, "llm", self.client_identifier, self.__client_passkey)
        embedding_port = ClientPort(self.base_url, "embedding", self.client_identifier, self.__client_passkey)
        system_port = ClientPort(self.base_url, "system", self.client_identifier, self.__client_passkey)
        diagnostics_port = ClientPort(self.base_url, "diagnostics", self.client_identifier, self.__client_passkey)

        self.llm = LLMNamespace(llm_port)
        self.embedding = EmbeddingNamespace(embedding_port)
        self.system = SystemNamespace(system_port)
        self.diagnostics = DiagnosticsNamespace(diagnostics_port)
        logger.debug("Finished initializing ports and namespaces.")

    # ensure you connect and close properly!
    def __init__(
        self,
        base_url: str | None,
        client_identifier: str | None,
        client_passkey: str | None,
    ):
        self.client_identifier = client_identifier or generate_random_base64(18)
        self.__client_passkey = client_passkey or generate_random_base64(18)
        self.base_url = base_url
