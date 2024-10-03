import json
import urllib.error
import urllib.request
from typing import Optional
from typing_extensions import override

import lmstudio_sdk.utils as utils

from .LMStudioClient import LMStudioClient


logger = utils.get_logger(__name__)


class SyncLMStudioClient(LMStudioClient):
    """Synchronous client for the LM Studio server.

    Intended to be a drop-in replacement for the OpenAI Python SDK.
    If you are porting code from TypeScript, are building an application
    with asyncio, or desire greater control over the event loop, consider
    using the asynchronous client instead.

    Do not construct this directly unless you know what you are doing.
    Instead, use the `LMStudioClient` factory function: it will return
    an instance of this class if called normally.

    Methods are dot accessed through the four namespaces:
    llm, embedding, system, and diagnostics. For example:

    ```python
    llm_client = LMStudioClient()

    print(llm_client.system.list_downloaded_models())

    model = llm_client.llm.get("qwen2")
    result = model.respond(
        [{"role": "user", "content": "Tell me a long story."}],
        {}
    )

    for completion in result:
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

    @override
    def _is_localhost_with_given_port_lmstudio_server(self, port: int) -> int:
        url = f"http://127.0.0.1:{port}/lmstudio-greeting"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status != 200:
                    raise ValueError("Status is not 200.")

                body = response.read().decode("utf-8")
                json_response = json.loads(body)
                if not json_response.get("lmstudio", False):
                    raise ValueError("Not an LM Studio server.")

                return port
        except (urllib.error.URLError, ValueError) as e:
            raise ValueError("Failed to connect to the server: %s", str(e))

    @override
    def _guess_base_url(self) -> str:
        for port in utils.lms_default_ports:
            try:
                successful_port = (
                    self._is_localhost_with_given_port_lmstudio_server(port)
                )
                logger.info(
                    "Found LM Studio server on localhost port %d.",
                    successful_port,
                )
                return f"ws://127.0.0.1:{successful_port}"
            except ValueError:
                logger.debug(
                    "Failed to connect to LM Studio on port %d.", port
                )
                continue

        logger.error(
            "Failed to connect to LM Studio on any of the default ports."
        )
        raise ValueError("""
            Failed to connect to LM Studio on any of the default ports.
            Is LM Studio running? If not, you can start it by running `lms server start`.
            (i) For more information, refer to the LM Studio documentation:
            https://lmstudio.ai/docs/local-server
        """)

    def __init__(
        self,
        base_url: Optional[str],
        client_identifier: Optional[str],
        client_passkey: Optional[str],
    ):
        super().__init__(base_url, client_identifier, client_passkey)

    @override
    def connect(self):
        if self.base_url is None:
            logger.warning("base_url is None. Attempting to guess base_url.")
            try:
                self.base_url = self._guess_base_url()
            except RuntimeError:
                logger.error(
                    "Failed to guess base_url. Is the LM Studio server running?"
                )
                raise ValueError(
                    "Failed to guess base_url. Is the LM Studio server running?"
                )
        self._validate_base_url_or_throw(self.base_url)

        self._create_ports(False)
        logger.info("Connecting to LM Studio server at %s...", self.base_url)
        try:
            self.llm.connect()
            logger.debug("LLM port connected, connecting to embedding port...")
            self.embedding.connect()
            logger.debug(
                "Embedding port connected, connecting to system port..."
            )
            self.system.connect()
            logger.debug(
                "System port connected, connecting to diagnostics port..."
            )
            self.diagnostics.connect()
            logger.info("Connected to LM Studio server.")
        except ConnectionRefusedError:
            logger.error(
                "Failed to connect to LM Studio server at %s.", self.base_url
            )
            raise ValueError(
                "Failed to connect to LM Studio server at %s.", self.base_url
            )

        return self

    @override
    def close(self):
        logger.info(
            "Closing connection to LM Studio server at %s...", self.base_url
        )
        self.llm.close()
        logger.debug("LLM port closed, closing embedding port...")
        self.embedding.close()
        logger.debug("Embedding port closed, closing system port...")
        self.system.close()
        logger.debug("System port closed, closing diagnostics port...")
        self.diagnostics.close()
        logger.info("Closed connection to LM Studio server.")
