import asyncio
import http.client
import json
import urllib.error
from typing import Optional
from typing_extensions import override


import lmstudio_sdk.utils as utils

from .LMStudioClient import LMStudioClient


logger = utils.get_logger(__name__)


class AsyncLMStudioClient(LMStudioClient):
    """Asynchronous client for the LM Studio server.

    A more faithful port of the TypeScript SDK: if you have code in
    TypeScript, it will translate almost directly to this client.
    If you are not familiar with asyncio or are adapting an application
    that used the OpenAI Python SDK, you may want to use the synchronous
    client instead.

    Do not construct this directly unless you know what you are doing.
    Instead, use the `LMStudioClient` factory function: it will return
    an instance of this class if `await`ed.

    Methods are dot accessed through the four namespaces:
    llm, embedding, system, and diagnostics. For example:

    ```python
    llm_client = await LMStudioClient()

    print(await llm_client.system.list_downloaded_models())

    model = await llm_client.llm.get("qwen2")
    result = await model.respond(
        [{"role": "user", "content": "Tell me a long story."}],
        {}
    )

    async for completion in result:
        print(completion)
    ```

    Attributes:
        client_identifier: Unique identifier for the client.
        base_url: Base URL for the LM Studio server.
        llm: Method namespace for interacting with LLM models.
        embedding: Method namespace for interacting with embedding models.
        system: Method namespace for LM Studio system functions.
        diagnostics: Method namespace for server diagnostics.
    """

    # TODO wait, why is this async? It's not doing anything async
    @override
    async def _is_localhost_with_given_port_lmstudio_server(
        self, port: int
    ) -> int:
        conn = http.client.HTTPConnection("127.0.0.1", port)
        try:
            conn.request("GET", "/lmstudio-greeting")
            response = conn.getresponse()

            if response.status != 200:
                raise ValueError("Status is not 200.")

            body = response.read().decode("utf-8")
            json_response = json.loads(body)
            if not json_response.get("lmstudio", False):
                raise ValueError("Not an LM Studio server.")

            return port
        except (urllib.error.URLError, ValueError) as e:
            logger.debug("Failed to connect to LM Studio on port %d.", port)
            raise ValueError("Failed to connect to the server: %s", str(e))
        finally:
            conn.close()

    @override
    async def _guess_base_url(self) -> str:
        try:
            port = await asyncio.wait_for(
                asyncio.gather(
                    *[
                        self._is_localhost_with_given_port_lmstudio_server(
                            port
                        )
                        for port in utils.lms_default_ports
                    ],
                    return_exceptions=True,
                ),
                timeout=10,
            )
            successful_port = next(p for p in port if isinstance(p, int))
            logger.info(
                "Found LM Studio server on localhost port %d.", successful_port
            )
            return f"ws://127.0.0.1:{successful_port}"
        except asyncio.TimeoutError:
            logger.error(
                "Failed to connect to LM Studio on any of the default ports."
            )
            raise ValueError(
                "Failed to connect to LM Studio on any of the default ports."
            )

    def __init__(
        self,
        base_url: Optional[str],
        client_identifier: Optional[str],
        client_passkey: Optional[str],
    ):
        super().__init__(base_url, client_identifier, client_passkey)

    @override
    async def connect(self):
        if self.base_url is None:
            logger.warning("base_url is None. Attempting to guess base_url.")
            try:
                self.base_url = await self._guess_base_url()
            except RuntimeError:
                logger.error(
                    "Failed to guess base_url. Is the LM Studio server running?"
                )
                raise ValueError(
                    "Failed to guess base_url. Is the LM Studio server running?"
                )
        self._validate_base_url_or_throw(self.base_url)

        self._create_ports(True)

        logger.info("Connecting to LM Studio server at %s...", self.base_url)
        try:
            await asyncio.gather(
                self.llm.connect(),
                self.embedding.connect(),
                self.system.connect(),
                self.diagnostics.connect(),
            )
        except ConnectionRefusedError:
            logger.error(
                "Failed to connect to LM Studio server at %s.", self.base_url
            )
            raise ValueError(
                "Failed to connect to LM Studio server at %s.", self.base_url
            )
        logger.info("Connected to LM Studio server.")

        return self

    @override
    async def close(self):
        logger.info(
            "Closing connection to LM Studio server at %s...", self.base_url
        )
        await asyncio.gather(
            self.llm.close(),
            self.embedding.close(),
            self.system.close(),
            self.diagnostics.close(),
        )
        logger.info("Closed connection to LM Studio server.")
