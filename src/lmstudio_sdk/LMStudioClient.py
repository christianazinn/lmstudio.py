import json
from secrets import token_bytes
from base64 import b64encode


from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError

from .lms_backend import ClientPort, DiagnosticsNamespace, EmbeddingNamespace, LLMNamespace, SystemNamespace
from .lms_dataclasses import LMStudioClientConstructorOpts


lms_default_ports = [1234]


def generate_random_base64(byte_length: int) -> str:
    random_bytes = token_bytes(byte_length)
    return b64encode(random_bytes).decode("utf-8")


class LMStudioClient:
    client_identifier: str
    base_url: str | None

    llm: LLMNamespace
    embedding: EmbeddingNamespace
    system: SystemNamespace
    diagnostics: DiagnosticsNamespace

    def __validate_base_url_or_throw(self, base_url):
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

    def __is_localhost_with_given_port_lmstudio_server(self, port: int) -> int:
        url = f"http://127.0.0.1:{port}/lmstudio-greeting"
        try:
            with urlopen(url, timeout=5) as response:
                if response.status != 200:
                    raise ValueError("Status is not 200.")

                body = response.read().decode("utf-8")
                json_response = json.loads(body)
                if not json_response.get("lmstudio", False):
                    raise ValueError("Not an LM Studio server.")

                return port
        except (URLError, ValueError) as e:
            raise ValueError(f"Failed to connect to the server: {str(e)}")

    def __guess_base_url(self, lms_default_ports) -> str:
        for port in lms_default_ports:
            try:
                successful_port = self.__is_localhost_with_given_port_lmstudio_server(port)
                return f"ws://127.0.0.1:{successful_port}"
            except ValueError:
                continue

        raise ValueError("""
            Failed to connect to LM Studio on any of the default ports.
            Is LM Studio running? If not, you can start it by running `lms server start`.
            (i) For more information, refer to the LM Studio documentation:
            https://lmstudio.ai/docs/local-server
        """)

    # ensure you connect and close properly!
    def __init__(self, opts: LMStudioClientConstructorOpts):
        self.client_identifier = opts.get("client_identifier", generate_random_base64(18))
        self.__client_passkey = opts.get("client_passkey", generate_random_base64(18))
        # TODO: guess base url is async???? fuck! figure out a better way to do this
        # for now logic is in connect()
        self.base_url = opts.get("base_url", None)
        if self.base_url is None:
            self.base_url = self.__guess_base_url()
        self.__validate_base_url_or_throw(self.base_url)

        # TODO LP: disambiguate ClientPorts so each ClientPort can only call particular endpoints
        llm_port = ClientPort(self.base_url, "llm", self.client_identifier, self.__client_passkey)
        embedding_port = ClientPort(self.base_url, "embedding", self.client_identifier, self.__client_passkey)
        system_port = ClientPort(self.base_url, "system", self.client_identifier, self.__client_passkey)
        diagnostics_port = ClientPort(self.base_url, "diagnostics", self.client_identifier, self.__client_passkey)

        self.llm = LLMNamespace(llm_port)
        self.embedding = EmbeddingNamespace(embedding_port)
        self.system = SystemNamespace(system_port)
        self.diagnostics = DiagnosticsNamespace(diagnostics_port)

        self.llm.connect()
        self.embedding.connect()
        self.system.connect()
        self.diagnostics.connect()

    def close(self):
        self.llm.close()
        self.embedding.close()
        self.system.close()
        self.diagnostics.close()