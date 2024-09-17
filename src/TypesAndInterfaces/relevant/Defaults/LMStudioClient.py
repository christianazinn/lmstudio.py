import asyncio
import json

from urllib.parse import urlparse
from http.client import HTTPConnection

from TypesAndInterfaces.relevant.Defaults.utils import generate_random_base64

from TypesAndInterfaces.relevant.Defaults.ClientPort import ClientPort

from TypesAndInterfaces.relevant.Namespaces.SystemNamespace import SystemNamespace
from TypesAndInterfaces.relevant.Namespaces.ModelNamespace import LLMNamespace
from TypesAndInterfaces.relevant.Namespaces.ModelNamespace import EmbeddingNamespace
from TypesAndInterfaces.irrelevant.DiagnosticsNamespace import DiagnosticsNamespace

from TypesAndInterfaces.relevant.CallOptions.LMStudioClientConstructorOpts import LMStudioClientConstructorOpts


lms_default_ports = [1234]


class LMStudioClient:
    client_identifier: str

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

    async def __is_localhost_with_given_port_lmstudio_server(self, port: int) -> int:
        url = f"http://127.0.0.1:{port}/lmstudio-greeting"
        parsed_url = urlparse(url)

        def fetch():
            conn = HTTPConnection(parsed_url.hostname, parsed_url.port)
            try:
                conn.request("GET", parsed_url.path)
                response = conn.getresponse()
                if response.status != 200:
                    raise ValueError("Status is not 200.")

                body = response.read().decode("utf-8")
                json_response = json.loads(body)
                if not json_response.get("lmstudio", False):
                    raise ValueError("Not an LM Studio server.")

                return port
            finally:
                conn.close()

        try:
            return await asyncio.to_thread(fetch)
        except Exception as e:
            raise ValueError(f"Failed to connect to the server: {str(e)}")

    async def __guess_base_url(self) -> str:
        try:
            port = await asyncio.wait_for(
                asyncio.gather(
                    *[self.__is_localhost_with_given_port_lmstudio_server(port) for port in lms_default_ports],
                    return_exceptions=True,
                ),
                timeout=10,  # Adjust timeout as needed
            )
            successful_port = next(p for p in port if isinstance(p, int))
            return f"ws://127.0.0.1:{successful_port}"
        except asyncio.TimeoutError:
            raise ValueError("""
                Failed to connect to LM Studio on the default port (1234).
                Is LM Studio running? If not, you can start it by running `lms server start`.
                (i) For more information, refer to the LM Studio documentation:
                https://lmstudio.ai/docs/local-server
            """)

    # python does not have async constructors so we do this
    @classmethod
    async def create(cls, opts: LMStudioClientConstructorOpts):
        client = cls(opts)
        await client.connect()
        return client

    # ensure you connect and close properly!
    def __init__(self, opts: LMStudioClientConstructorOpts):
        opts = LMStudioClientConstructorOpts.model_validate(opts)
        self.client_identifier = opts.get("client_identifier", generate_random_base64(18))
        client_passkey = opts.get("client_passkey", generate_random_base64(18))
        base_url = opts.get("base_url", self.__guess_base_url())
        self.__validate_base_url_or_throw(base_url)

        # TODO LP: disambiguate ClientPorts so each ClientPort can only call particular endpoints
        llm_port = ClientPort(base_url, "llm", self.client_identifier, client_passkey)
        embedding_port = ClientPort(base_url, "embedding", self.client_identifier, client_passkey)
        system_port = ClientPort(base_url, "system", self.client_identifier, client_passkey)
        diagnostics_port = ClientPort(base_url, "diagnostics", self.client_identifier, client_passkey)

        self.llm = LLMNamespace(llm_port)
        self.embedding = EmbeddingNamespace(embedding_port)
        self.system = SystemNamespace(system_port)
        self.diagnostics = DiagnosticsNamespace(diagnostics_port)

    async def connect(self):
        await self.llm.connect()
        await self.embedding.connect()
        await self.system.connect()
        await self.diagnostics.connect()

    async def close(self):
        await self.llm.close()
        await self.embedding.close()
        await self.system.close()
        await self.diagnostics.close()
