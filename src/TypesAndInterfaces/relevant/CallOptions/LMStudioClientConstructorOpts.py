from typing import Optional, Protocol, Any
from pydantic import Field
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class LoggerInterface(Protocol):
    def info(self, *messages: Any) -> None: ...
    def error(self, *messages: Any) -> None: ...
    def warn(self, *messages: Any) -> None: ...
    def debug(self, *messages: Any) -> None: ...


class LMStudioClientConstructorOpts(ConfiguredBaseModel):
    # TODO Pydantic does not like Protocol
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
