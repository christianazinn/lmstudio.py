from typing import NotRequired, Protocol, Any
from typing_extensions import TypedDict


class LoggerInterface(Protocol):
    def info(self, *messages: Any) -> None: ...
    def error(self, *messages: Any) -> None: ...
    def warn(self, *messages: Any) -> None: ...
    def debug(self, *messages: Any) -> None: ...


class LMStudioClientConstructorOpts(TypedDict):
    logger: NotRequired[LoggerInterface]
    """
    Changes the logger that is used by LMStudioClient internally. The default logger is `console`.
    By default, LMStudioClient only logs warnings and errors that require user intervention. If the
    `verbose` option is enabled while calling supporting methods, those messages will also be
    directed to the specified logger.
    """

    base_url: NotRequired[str]
    """
    The base URL of the LM Studio server. If not provided, LM Studio will attempt to connect to the
    localhost with various default ports.

    If you have set a custom port and/or are reverse-proxying, you should pass in the base_url.

    Since LM Studio uses WebSockets, the protocol must be "ws" or "wss".

    For example, if have changed the port to 8080, you should create the LMStudioClient like so:

    ```python
    client = LMStudioClient(base_url="ws://127.0.0.1:8080")
    ```
    """

    verbose_error_messages: NotRequired[bool]
    """
    Whether to include stack traces in the errors caused by LM Studio. By default, this is set to
    `False`. If set to `True`, LM Studio SDK will include a stack trace in the error message.
    """

    client_identifier: NotRequired[str]
    """
    Changes the client identifier used to authenticate with LM Studio. By default, it uses a
    randomly generated string.

    If you wish to share resources across multiple LMStudioClient, you should set them to use the
    same `client_identifier` and `client_passkey`.
    """

    client_passkey: NotRequired[str]
    """
    Changes the client passkey used to authenticate with LM Studio. By default, it uses a randomly
    generated string.

    If you wish to share resources across multiple LMStudioClient, you should set them to use the
    same `client_identifier` and `client_passkey`.
    """
