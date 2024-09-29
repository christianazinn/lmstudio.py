import asyncio
import json
from http.client import HTTPConnection
from typing import Optional
from urllib.error import URLError

from ...utils import lms_default_ports, get_logger
from .LMStudioClient import LMStudioClient


logger = get_logger(__name__)


class AsyncLMStudioClient(LMStudioClient):
    async def _is_localhost_with_given_port_lmstudio_server(
        self, port: int
    ) -> int:
        conn = HTTPConnection("127.0.0.1", port)
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
        except (URLError, ValueError) as e:
            raise ValueError(f"Failed to connect to the server: {str(e)}")
        finally:
            conn.close()

    async def _guess_base_url(self) -> str:
        try:
            port = await asyncio.wait_for(
                asyncio.gather(
                    *[
                        self._is_localhost_with_given_port_lmstudio_server(port)
                        for port in lms_default_ports
                    ],
                    return_exceptions=True,
                ),
                timeout=10,  # Adjust timeout as needed
            )
            successful_port = next(p for p in port if isinstance(p, int))
            logger.info(
                f"Found LM Studio server on localhost port {successful_port}."
            )
            return f"ws://127.0.0.1:{successful_port}"
        except asyncio.TimeoutError:
            logger.error(
                "Failed to connect to LM Studio on any of the default ports."
            )
            raise ValueError("""
                Failed to connect to LM Studio on the default port (1234).
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

    async def connect(self):
        if self.base_url is None:
            logger.warning("base_url is None. Attempting to guess base_url.")
            self.base_url = await self._guess_base_url()
        self._validate_base_url_or_throw(self.base_url)

        self._create_ports(True)

        logger.info(f"Connecting to LM Studio server at {self.base_url}...")
        try:
            await asyncio.gather(
                self.llm.connect(),
                self.embedding.connect(),
                self.system.connect(),
                self.diagnostics.connect(),
            )
        except ConnectionRefusedError:
            logger.error(
                f"Failed to connect to LM Studio server at {self.base_url}."
            )
            raise ValueError(
                f"Failed to connect to LM Studio server at {self.base_url}."
            )
        logger.info("Connected to LM Studio server.")

        return self

    async def close(self):
        logger.info(
            f"Closing connection to LM Studio server at {self.base_url}..."
        )
        await asyncio.gather(
            self.llm.close(),
            self.embedding.close(),
            self.system.close(),
            self.diagnostics.close(),
        )
        logger.info("Closed connection to LM Studio server.")
