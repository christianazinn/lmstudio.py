from typing import Callable, Generic, NotRequired, TypedDict, TypeVar, Union
from enum import Enum
from ...utils import AbortSignal


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


TLoadModelConfig = TypeVar("TLoadModelConfig")


class BaseLoadModelOpts(TypedDict, Generic[TLoadModelConfig]):
    identifier: NotRequired[str]
    """
    The identifier to use for the loaded model.

    By default, the identifier is the same as the path (1st parameter). If the identifier already
    exists, a number will be attached. This option allows you to specify the identifier to use.

    However, when the identifier is specified and it is in use, an error will be thrown. If the
    call is successful, it is guaranteed that the loaded model will have the specified identifier.
    """

    config: NotRequired[TLoadModelConfig]
    """
    The configuration to use when loading the model.
    """

    signal: NotRequired[AbortSignal]
    """
    An `AbortSignal` to cancel the model loading. This is useful if you wish to add a functionality
    to cancel the model loading.

    Example usage:

    ```python
    import asyncio

    async def load_model():
        ac = asyncio.get_event_loop().create_future()
        model = await client.llm.load(
            model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
            signal=ac
        )

        # Later, to cancel the model loading
        ac.cancel()
    ```

    AbortSignal is the Python equivalent of JavaScript's AbortSignal for cancelling asynchronous operations.
    """

    # TODO: in TS verbose would default to False, so make sure to handle this
    verbose: NotRequired[Union[bool, LogLevel]]
    """
    Controls the logging of model loading progress.

    - If set to `True`, logs progress at the "info" level.
    - If set to `False`, no logs are emitted.
    - If a specific logging level is desired, it can be provided as a LogLevel enum value.

    Logs are directed to the logger specified during the `LMStudioClient` construction.

    Progress logs will be disabled if an `on_progress` callback is provided.

    Default value is LogLevel.INFO, which logs progress at the "info" level.
    """

    on_progress: NotRequired[Callable[[float], None]]
    """
    A function that is called with the progress of the model loading. The function is called with a
    number between 0 and 1, inclusive, representing the progress of the model loading.

    If an `on_progress` callback is provided, verbose progress logs will be disabled.
    """
