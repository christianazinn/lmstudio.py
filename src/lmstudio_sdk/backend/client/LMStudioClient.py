import urllib.parse
from abc import ABC, abstractmethod
from typing import Optional

import lmstudio_sdk.utils as utils
import lmstudio_sdk.backend.communications as comms
import lmstudio_sdk.backend.namespaces as ns


logger = utils.get_logger(__name__)


class LMStudioClient(ABC):
    client_identifier: str
    """Unique identifier for the client."""

    base_url: Optional[str]
    """Base URL for the LM Studio server."""

    llm: ns.LLMNamespace = None
    """Method namespace for interacting with LLM models."""

    embedding: ns.EmbeddingNamespace = None
    """Method namespace for interacting with embedding models."""

    system: ns.SystemNamespace = None
    """Method namespace for LM Studio system functions."""

    diagnostics: ns.DiagnosticsNamespace = None
    """Method namespace for server diagnostics."""

    def _validate_base_url_or_throw(self, base_url):
        error_msg = None
        error_info = None
        try:
            url = urllib.parse.urlparse(base_url)
        except ValueError:
            error_msg = "Failed to construct LMStudioClient. \
                The baseUrl passed in is invalid. Received: %s"
            error_info = base_url
            logger.error(error_msg, error_info)
            raise ValueError(error_msg, error_info)

        if url.scheme not in ["ws", "wss"]:
            error_msg = "Failed to construct LMStudioClient. \
                The baseUrl passed in must have protocol 'ws' or 'wss'. \
                Received: %s."
            error_info = url.scheme

        elif url.query:
            error_msg = "Failed to construct LMStudioClient. \
                The baseUrl passed contains search parameters ('%s')."
            error_info = url.query

        elif url.fragment:
            error_msg = "Failed to construct LMStudioClient. \
                The baseUrl passed contains a hash ('%s')."
            error_info = url.fragment

        elif url.username or url.password:
            error_msg = "Failed to construct LMStudioClient. \
                The baseUrl passed contains a username or password. \
                We do not support these in the baseUrl. Received: %s"
            error_info = url.username

        elif base_url.endswith("/"):
            error_msg = "Failed to construct LMStudioClient. \
                The baseUrl passed in must not end with a '/'. \
                If you are reverse-proxying, you should remove \
                the trailing slash from the baseUrl. Received: %s"
            error_info = base_url

        if error_msg and error_info:
            logger.error(error_msg, error_info)
            raise ValueError(error_msg, error_info)

    @abstractmethod
    def _is_localhost_with_given_port_lmstudio_server(self, port: int) -> int:
        pass

    @abstractmethod
    def _guess_base_url(self) -> str:
        pass

    @abstractmethod
    def connect(self):
        """Connect to the LM Studio server on all ports.

        Raises:
            ValueError: If the connection cannot be established.
        """
        pass

    @abstractmethod
    def close(self):
        """Close the connection to the LM Studio server on all ports."""
        pass

    def _create_ports(self, is_async: bool):
        """Create ports for the client.

        Args:
            is_async (bool): Whether to create async or sync ports.

        Raises:
            ValueError: If the base_url, client_identifier,
                or client_passkey is None.
        """
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
            ClientPort = comms.AsyncClientPort
        else:
            ClientPort = comms.SyncClientPort
        logger.info(
            "Creating %s ports at %s as %s...",
            "async" if is_async else "sync",
            self.base_url,
            self.client_identifier,
        )

        llm_port = ClientPort(
            self.base_url, "llm", self.client_identifier, self.__client_passkey
        )
        embedding_port = ClientPort(
            self.base_url,
            "embedding",
            self.client_identifier,
            self.__client_passkey,
        )
        system_port = ClientPort(
            self.base_url,
            "system",
            self.client_identifier,
            self.__client_passkey,
        )
        diagnostics_port = ClientPort(
            self.base_url,
            "diagnostics",
            self.client_identifier,
            self.__client_passkey,
        )

        self.llm = ns.LLMNamespace(llm_port)
        self.embedding = ns.EmbeddingNamespace(embedding_port)
        self.system = ns.SystemNamespace(system_port)
        self.diagnostics = ns.DiagnosticsNamespace(diagnostics_port)
        logger.debug("Finished initializing ports and namespaces.")

    # ensure you connect and close properly!
    def __init__(
        self,
        base_url: Optional[str],
        client_identifier: Optional[str],
        client_passkey: Optional[str],
    ):
        self.client_identifier = (
            client_identifier or utils.generate_random_base64(18)
        )
        self.__client_passkey = client_passkey or utils.generate_random_base64(
            18
        )
        self.base_url = base_url
