from typing import Callable, Generic, NotRequired, TypedDict, TypeVar, Union

import lmstudio_sdk.utils as utils


TLoadModelConfig = TypeVar("TLoadModelConfig")


class BaseLoadModelOpts(TypedDict, Generic[TLoadModelConfig]):
    """Base options for loading a model."""

    identifier: NotRequired[str]
    """The identifier to use for the loaded model.

    By default, the identifier is the same as the path (1st parameter).
    If the identifier already exists, a number will be attached.
    This option allows you to specify the identifier to use.

    However, when the identifier is specified and it is in use,
    an error will be thrown. If the call is successful, it is guaranteed
    that the loaded model will have the specified identifier.
    """

    config: NotRequired[TLoadModelConfig]
    """The configuration to use when loading the model."""

    signal: NotRequired[Union[utils.AsyncAbortSignal, utils.SyncAbortSignal]]
    """An `AbortSignal` to cancel the model loading.

    This is useful if you wish to add a functionality to cancel the model loading.

    Example usage:

    ```python
    from lmstudio_sdk.utils import AsyncAbortSignal

    async def load_model():
        ac = AsyncAbortSignal()
        model = await client.llm.load(
            "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
            {"signal": ac}
        )

        # Later, to cancel the model loading
        ac.cancel()
    ```
    """

    on_progress: NotRequired[Callable[[float], None]]
    """A callback to receive progress updates.

    Called with a number between 0 and 1, inclusive,
    representing the progress of the model loading.

    If an `on_progress` callback is provided,
    verbose progress logs will be disabled.
    """
