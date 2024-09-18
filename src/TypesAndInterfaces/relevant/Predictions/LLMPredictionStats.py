from enum import Enum
from typing import Optional
from pydantic import Field
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class LLMPredictionStopReason(str, Enum):
    """
    Represents the reason why a prediction stopped. Only the following values are possible:

    - `userStopped`: The user stopped the prediction. This includes calling the `cancel` method on
      the `OngoingPrediction` object.
    - `modelUnloaded`: The model was unloaded during the prediction.
    - `failed`: An error occurred during the prediction.
    - `eosFound`: The model predicted an end-of-sequence token, which is a way for the model to
      indicate that it "thinks" the sequence is complete.
    - `stopStringFound`: A stop string was found in the prediction. (Stop strings can be specified
      with the `stopStrings` config option. This stop reason will only occur if the `stopStrings`
      config option is set to an array of strings.)
    - `maxPredictedTokensReached`: The maximum number of tokens to predict was reached. (Length limit
      can be specified with the `maxPredictedTokens` config option. This stop reason will only occur
      if the `maxPredictedTokens` config option is set to a value other than -1.)
    - `contextLengthReached`: The context length was reached. This stop reason will only occur if the
      `contextOverflowPolicy` is set to `stopAtLimit`.
    """

    USER_STOPPED = "userStopped"
    MODEL_UNLOADED = "modelUnloaded"
    FAILED = "failed"
    EOS_FOUND = "eosFound"
    STOP_STRING_FOUND = "stopStringFound"
    MAX_PREDICTED_TOKENS_REACHED = "maxPredictedTokensReached"
    CONTEXT_LENGTH_REACHED = "contextLengthReached"


class LLMPredictionStats(ConfiguredBaseModel):
    """
    @public
    """

    stop_reason: LLMPredictionStopReason = Field(
        ...,
        description="""
    The reason why the prediction stopped.

    This is a string enum with the following possible values:

    - `userStopped`: The user stopped the prediction. This includes calling the `cancel` method on
      the `OngoingPrediction` object.
    - `modelUnloaded`: The model was unloaded during the prediction.
    - `failed`: An error occurred during the prediction.
    - `eosFound`: The model predicted an end-of-sequence token, which is a way for the model to
      indicate that it "thinks" the sequence is complete.
    - `stopStringFound`: A stop string was found in the prediction. (Stop strings can be specified
      with the `stopStrings` config option. This stop reason will only occur if the `stopStrings`
      config option is set.)
    - `maxPredictedTokensReached`: The maximum number of tokens to predict was reached. (Length
      limit can be specified with the `maxPredictedTokens` config option. This stop reason will
      only occur if the `maxPredictedTokens` config option is set to a value other than -1.)
    - `contextLengthReached`: The context length was reached. This stop reason will only occur if
      the `contextOverflowPolicy` is set to `stopAtLimit`.
    """,
    )

    tokens_per_second: Optional[float] = Field(
        default=None,
        description="""
    The average number of tokens predicted per second.

    Note: This value can be None in the case of a very short prediction which results in a
    NaN or a Infinity value.
    """,
    )

    num_gpu_layers: Optional[int] = Field(default=None, description="The number of GPU layers used in the prediction.")

    time_to_first_token_sec: Optional[float] = Field(
        default=None, description="The time it took to predict the first token in seconds."
    )

    prompt_tokens_count: Optional[int] = Field(default=None, description="The number of tokens that were supplied.")

    predicted_tokens_count: Optional[int] = Field(default=None, description="The number of tokens that were predicted.")

    total_tokens_count: Optional[int] = Field(
        default=None,
        description="""
    The total number of tokens. This is the sum of the prompt tokens and the predicted tokens.
    """,
    )
