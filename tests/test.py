import asyncio
import json
from urllib.parse import urlparse
from http.client import HTTPConnection
from typing import Optional, Protocol, Any
from pydantic import BaseModel, Field


class LoggerInterface(Protocol):
    def info(self, *messages: Any) -> None: ...
    def error(self, *messages: Any) -> None: ...
    def warn(self, *messages: Any) -> None: ...
    def debug(self, *messages: Any) -> None: ...


class LMStudioClientConstructorOpts(BaseModel):
    logger: Optional[Any] = Field(
        default=None,
        description="""
    Changes the logger that is used by LMStudioClient internally. The default logger is `console`.
    By default, LMStudioClient only logs warnings and errors that require user intervention. If the
    `verbose` option is enabled while calling supporting methods, those messages will also be
    directed to the specified logger.
    """,
    )

    base_url: Optional[str] = Field(
        default=None,
        description="""
    The base URL of the LM Studio server. If not provided, LM Studio will attempt to connect to the
    localhost with various default ports.

    If you have set a custom port and/or are reverse-proxying, you should pass in the base_url.

    Since LM Studio uses WebSockets, the protocol must be "ws" or "wss".

    For example, if have changed the port to 8080, you should create the LMStudioClient like so:

    ```python
    client = LMStudioClient(base_url="ws://127.0.0.1:8080")
    ```
    """,
    )

    verbose_error_messages: bool = Field(
        default=False,
        description="""
    Whether to include stack traces in the errors caused by LM Studio. By default, this is set to
    `False`. If set to `True`, LM Studio SDK will include a stack trace in the error message.
    """,
    )

    client_identifier: Optional[str] = Field(
        default=None,
        description="""
    Changes the client identifier used to authenticate with LM Studio. By default, it uses a
    randomly generated string.

    If you wish to share resources across multiple LMStudioClient, you should set them to use the
    same `client_identifier` and `client_passkey`.
    """,
    )

    client_passkey: Optional[str] = Field(
        default=None,
        description="""
    Changes the client passkey used to authenticate with LM Studio. By default, it uses a randomly
    generated string.

    If you wish to share resources across multiple LMStudioClient, you should set them to use the
    same `client_identifier` and `client_passkey`.
    """,
    )

    class Config:
        extra = "forbid"


async def __is_localhost_with_given_port_lmstudio_server(port: int) -> int:
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


async def guess_base_url(opts: LMStudioClientConstructorOpts) -> str:
    opts = LMStudioClientConstructorOpts.model_validate(opts)
    try:
        port = await asyncio.wait_for(
            asyncio.gather(
                *[__is_localhost_with_given_port_lmstudio_server(port) for port in [1234]],
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


async def main():
    print(await guess_base_url({"bae_url": "ws://localhost:1234/system"}))


if __name__ == "__main__":
    asyncio.run(main())
