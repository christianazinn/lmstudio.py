from typing import NotRequired, List, Callable
from typing_extensions import TypedDict
from TypesAndInterfaces.relevant.LLMGeneralSettings.LLMChatHistory import LLMContextOverflowPolicy
from TypesAndInterfaces.relevant.LLMGeneralSettings.LLMStructuredPredictionSetting import LLMStructuredPredictionSetting


class LLMPredictionConfig(TypedDict):
    """
    Shared config for running predictions on an LLM.
    """

    maxPredictedTokens: NotRequired[int]
    """
    Number of tokens to predict at most. If set to -1, the model will predict as many tokens as it
    wants.

    When the prediction is stopped because of this limit, the `stopReason` in the prediction stats
    will be set to `maxPredictedTokensReached`.

    See `LLMPredictionStopReason` for other reasons that a prediction might stop.
    """

    temperature: NotRequired[float]
    """
    The temperature parameter for the prediction model. A higher value makes the predictions more
    random, while a lower value makes the predictions more deterministic. The value should be
    between 0 and 1.
    """

    stopStrings: NotRequired[List[str]]
    """
    An array of strings. If the model generates one of these strings, the prediction will stop.

    When the prediction is stopped because of this limit, the `stopReason` in the prediction stats
    will be set to `stopStringFound`.

    See `LLMPredictionStopReason` for other reasons that a prediction might stop.
    """

    contextOverflowPolicy: NotRequired[LLMContextOverflowPolicy]
    """
    The behavior for when the generated tokens length exceeds the context window size. The allowed
    values are:

    - `stopAtLimit`: Stop the prediction when the generated tokens length exceeds the context
      window size. If the generation is stopped because of this limit, the `stopReason` in the
      prediction stats will be set to `contextLengthReached`
    - `truncateMiddle`: Keep the system prompt and the first user message, truncate middle.
    - `rollingWindow`: Maintain a rolling window and truncate past messages.
    """

    structured: NotRequired[LLMStructuredPredictionSetting]
    topKSampling: NotRequired[int]
    repeatPenalty: NotRequired[float]
    minPSampling: NotRequired[float]
    topPSampling: NotRequired[float]
    cpuThreads: NotRequired[int]


class LLMPredictionExtraOpts(TypedDict):
    on_prompt_processing_progress: NotRequired[Callable[[float], None]]
    """
    A callback that is called when the model is processing the prompt. The callback is called with
    a number between 0 and 1, representing the progress of the prompt processing.

    Prompt processing progress callbacks will only be called before the first token is emitted.
    """

    on_first_token: NotRequired[Callable[[], None]]
    """
    A callback that is called when the model has output the first token.
    """


class LLMPredictionOpts(LLMPredictionConfig, LLMPredictionExtraOpts):
    """
    Shared options for any prediction methods (`.complete`/`.respond`).

    Note, this class extends the `LLMPredictionConfig` class, which contains parameters that
    you can override for the LLM. See `LLMPredictionConfig` for more information.
    """

    pass
