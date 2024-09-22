from abc import ABC, abstractmethod


from urllib.parse import urlparse
from ...utils import generate_random_base64
from ..namespaces import DiagnosticsNamespace, EmbeddingNamespace, LLMNamespace, SystemNamespace


class LMStudioClient(ABC):
    client_identifier: str
    base_url: str | None
    verbose_error_messages: bool

    llm: LLMNamespace = None
    embedding: EmbeddingNamespace = None
    system: SystemNamespace = None
    diagnostics: DiagnosticsNamespace = None

    def _validate_base_url_or_throw(self, base_url):
        try:
            url = urlparse(base_url)
        except ValueError:
            raise ValueError(f"""
                    Failed to construct LMStudioClient. The baseUrl passed in is invalid. Received: {base_url}
                """)

        if url.scheme not in ["ws", "wss"]:
            raise ValueError(f"""
                    Failed to construct LMStudioClient. The baseUrl passed in must have protocol "ws" or "wss".
                    Received: {base_url}
                """)

        if url.query:
            raise ValueError(f"""
                    Failed to construct LMStudioClient. The baseUrl passed contains search parameters
                    ("{url.query}").
                """)

        if url.fragment:
            raise ValueError(f"""
                    Failed to construct LMStudioClient. The baseUrl passed contains a hash ("{url.fragment}").
                """)

        if url.username or url.password:
            raise ValueError(f"""
                    Failed to construct LMStudioClient. The baseUrl passed contains a username or password. We
                    do not support these in the baseUrl. Received: {base_url}
                """)

        if base_url.endswith("/"):
            raise ValueError(f"""
                    Failed to construct LMStudioClient. The baseUrl passed in must not end with a "/". If you
                    are reverse-proxying, you should remove the trailing slash from the baseUrl. Received:
                    {base_url}
                """)

    @abstractmethod
    def _is_localhost_with_given_port_lmstudio_server(self, port: int) -> int:
        pass

    @abstractmethod
    def _guess_base_url(self) -> str:
        pass

    @abstractmethod
    def close(self):
        pass

    def create_ports(self, is_async: bool):
        assert self.base_url is not None
        assert self.client_identifier is not None
        assert self.__client_passkey is not None

        if is_async:
            from ..communications import AsyncClientPort as ClientPort
        else:
            from ..communications import ClientPort

        # TODO LP: disambiguate ClientPorts so each ClientPort can only call particular endpoints
        llm_port = ClientPort(self.base_url, "llm", self.client_identifier, self.__client_passkey)
        embedding_port = ClientPort(self.base_url, "embedding", self.client_identifier, self.__client_passkey)
        system_port = ClientPort(self.base_url, "system", self.client_identifier, self.__client_passkey)
        diagnostics_port = ClientPort(self.base_url, "diagnostics", self.client_identifier, self.__client_passkey)

        self.llm = LLMNamespace(llm_port)
        self.embedding = EmbeddingNamespace(embedding_port)
        self.system = SystemNamespace(system_port)
        self.diagnostics = DiagnosticsNamespace(diagnostics_port)

    # ensure you connect and close properly!
    def __init__(
        self,
        base_url: str | None,
        # TODO do something with me
        verbose_error_messages: bool,
        client_identifier: str | None,
        client_passkey: str | None,
    ):
        self.client_identifier = client_identifier or generate_random_base64(18)
        self.__client_passkey = client_passkey or generate_random_base64(18)
        self.base_url = base_url
        self.verbose_error_messages = verbose_error_messages
