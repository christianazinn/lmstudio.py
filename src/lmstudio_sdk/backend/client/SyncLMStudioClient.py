import json
from urllib.request import urlopen
from urllib.error import URLError

from ...utils import lms_default_ports, get_logger
from .LMStudioClient import LMStudioClient


logger = get_logger(__name__)


class SyncLMStudioClient(LMStudioClient):
    def _is_localhost_with_given_port_lmstudio_server(self, port: int) -> int:
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

    def _guess_base_url(self) -> str:
        for port in lms_default_ports:
            try:
                successful_port = self._is_localhost_with_given_port_lmstudio_server(port)
                logger.info(f"Found LM Studio server on localhost port {successful_port}.")
                return f"ws://127.0.0.1:{successful_port}"
            except ValueError:
                logger.debug(f"Failed to connect to LM Studio on port {port}.")
                continue

        logger.error("Failed to connect to LM Studio on any of the default ports.")
        raise ValueError("""
            Failed to connect to LM Studio on any of the default ports.
            Is LM Studio running? If not, you can start it by running `lms server start`.
            (i) For more information, refer to the LM Studio documentation:
            https://lmstudio.ai/docs/local-server
        """)

    def __init__(
        self,
        base_url: str | None,
        client_identifier: str | None,
        client_passkey: str | None,
    ):
        super().__init__(base_url, client_identifier, client_passkey)
        if self.base_url is None:
            logger.warning("base_url is None. Attempting to guess base_url.")
            self.base_url = self._guess_base_url()
        self._validate_base_url_or_throw(self.base_url)

        self.create_ports(False)

        logger.info(f"Connecting to LM Studio server at {self.base_url}...")
        self.llm.connect()
        logger.debug("LLM port connected, connecting to embedding port...")
        self.embedding.connect()
        logger.debug("Embedding port connected, connecting to system port...")
        self.system.connect()
        logger.debug("System port connected, connecting to diagnostics port...")
        self.diagnostics.connect()
        logger.info("Connected to LM Studio server.")

    def close(self):
        logger.info(f"Closing connection to LM Studio server at {self.base_url}...")
        self.llm.close()
        logger.debug("LLM port closed, closing embedding port...")
        self.embedding.close()
        logger.debug("Embedding port closed, closing system port...")
        self.system.close()
        logger.debug("System port closed, closing diagnostics port...")
        self.diagnostics.close()
        logger.info("Closed connection to LM Studio server.")
