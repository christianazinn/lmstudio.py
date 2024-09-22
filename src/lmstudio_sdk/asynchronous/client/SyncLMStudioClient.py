import json

from urllib.request import urlopen
from urllib.error import URLError

from ...common import LMStudioClientConstructorOpts, lms_default_ports
from .LMStudioClient import LMStudioClient


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
                return f"ws://127.0.0.1:{successful_port}"
            except ValueError:
                continue

        raise ValueError("""
            Failed to connect to LM Studio on any of the default ports.
            Is LM Studio running? If not, you can start it by running `lms server start`.
            (i) For more information, refer to the LM Studio documentation:
            https://lmstudio.ai/docs/local-server
        """)

    def __init__(self, opts: LMStudioClientConstructorOpts | None):
        super().__init__(opts)
        if self.base_url is None:
            self.base_url = self._guess_base_url()
        self._validate_base_url_or_throw(self.base_url)

        self.create_ports()

        self.llm.connect()
        self.embedding.connect()
        self.system.connect()
        self.diagnostics.connect()

    def close(self):
        self.llm.close()
        self.embedding.close()
        self.system.close()
        self.diagnostics.close()
