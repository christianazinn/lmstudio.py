from typing import Optional, List, Callable
from pydantic import Field
from LLMGeneralSettings.LLMChatHistory import LLMContextOverflowPolicy
from LLMGeneralSettings.LLMStructuredPredictionSetting import LLMStructuredPredictionSetting
from Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class LLMPredictionConfig(ConfiguredBaseModel):
    """
    Shared config for running predictions on an LLM.
    """

    maxPredictedTokens: Optional[int] = Field(
        default=None,
        description="""
    Number of tokens to predict at most. If set to -1, the model will predict as many tokens as it
    wants.

    When the prediction is stopped because of this limit, the `stopReason` in the prediction stats
    will be set to `maxPredictedTokensReached`.

    See `LLMPredictionStopReason` for other reasons that a prediction might stop.
    """,
    )

    temperature: Optional[float] = Field(
        default=None,
        description="""
    The temperature parameter for the prediction model. A higher value makes the predictions more
    random, while a lower value makes the predictions more deterministic. The value should be
    between 0 and 1.
    """,
    )

    stopStrings: Optional[List[str]] = Field(
        default=None,
        description="""
    An array of strings. If the model generates one of these strings, the prediction will stop.

    When the prediction is stopped because of this limit, the `stopReason` in the prediction stats
    will be set to `stopStringFound`.

    See `LLMPredictionStopReason` for other reasons that a prediction might stop.
    """,
    )

    contextOverflowPolicy: Optional[LLMContextOverflowPolicy] = Field(
        default=None,
        description="""
    The behavior for when the generated tokens length exceeds the context window size. The allowed
    values are:

    - `stopAtLimit`: Stop the prediction when the generated tokens length exceeds the context
      window size. If the generation is stopped because of this limit, the `stopReason` in the
      prediction stats will be set to `contextLengthReached`
    - `truncateMiddle`: Keep the system prompt and the first user message, truncate middle.
    - `rollingWindow`: Maintain a rolling window and truncate past messages.
    """,
    )

    structured: Optional[LLMStructuredPredictionSetting] = Field(default=None, description="TODO: Documentation")
    topKSampling: Optional[int] = Field(default=None, description="TODO: Documentation")
    repeatPenalty: Optional[float] = Field(default=None, description="TODO: Documentation")
    minPSampling: Optional[float] = Field(default=None, description="TODO: Documentation")
    topPSampling: Optional[float] = Field(default=None, description="TODO: Documentation")
    cpuThreads: Optional[int] = Field(default=None, description="TODO: Documentation")


class LLMPredictionOpts(LLMPredictionConfig):
    """
    Shared options for any prediction methods (`.complete`/`.respond`).

    Note, this class extends the `LLMPredictionConfig` class, which contains parameters that
    you can override for the LLM. See `LLMPredictionConfig` for more information.
    """

    on_prompt_processing_progress: Optional[Callable[[float], None]] = Field(
        default=None,
        description="""
    A callback that is called when the model is processing the prompt. The callback is called with
    a number between 0 and 1, representing the progress of the prompt processing.

    Prompt processing progress callbacks will only be called before the first token is emitted.
    """,
    )

    on_first_token: Optional[Callable[[], None]] = Field(
        default=None,
        description="""
    A callback that is called when the model has output the first token.
    """,
    )
