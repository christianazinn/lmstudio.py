import enum
from typing import Optional


class LLMPredictionStopReason(str, enum.Enum):
    """The reason why a prediction stopped.

    Only the following values are possible:

    - `userStopped`: The user stopped the prediction.
      This includes calling the `cancel` method
      on the `OngoingPrediction` object.
    - `modelUnloaded`: The model was unloaded during the prediction.
    - `failed`: An error occurred during the prediction.
    - `eosFound`: The model predicted an end-of-sequence token,
      which is a way for the model to indicate that it "thinks"
      the sequence is complete.
    - `stopStringFound`: A stop string was found in the prediction.
      Stop strings can be specified with the `stop_strings` config option.
      This stop reason will only occur if the `stop_strings`
      config option is set to an array of strings.
    - `maxPredictedTokensReached`: The maximum number of tokens to predict
      was reached. Length limit can be specified with the `maxPredictedTokens`
      config option. This stop reason will only occur if
      the `maxPredictedTokens` config option is set to a value other than -1.
    - `contextLengthReached`: The context length was reached.
      This stop reason will only occur if the `context_overflow_policy`
      is set to `stopAtLimit`.
    """

    USER_STOPPED = "userStopped"
    MODEL_UNLOADED = "modelUnloaded"
    FAILED = "failed"
    EOS_FOUND = "eosFound"
    STOP_STRING_FOUND = "stopStringFound"
    MAX_PREDICTED_TOKENS_REACHED = "maxPredictedTokensReached"
    CONTEXT_LENGTH_REACHED = "contextLengthReached"


class LLMPredictionStats:
    """Statistics about a prediction."""

    stop_reason: LLMPredictionStopReason
    """The reason why the prediction stopped.

    Only the following values are possible:

    - `userStopped`: The user stopped the prediction.
      This includes calling the `cancel` method
      on the `OngoingPrediction` object.
    - `modelUnloaded`: The model was unloaded during the prediction.
    - `failed`: An error occurred during the prediction.
    - `eosFound`: The model predicted an end-of-sequence token,
      which is a way for the model to indicate that it "thinks"
      the sequence is complete.
    - `stopStringFound`: A stop string was found in the prediction.
      Stop strings can be specified with the `stop_strings` config option.
      This stop reason will only occur if the `stop_strings`
      config option is set to an array of strings.
    - `maxPredictedTokensReached`: The maximum number of tokens to predict
      was reached. Length limit can be specified with the `maxPredictedTokens`
      config option. This stop reason will only occur if
      the `maxPredictedTokens` config option is set to a value other than -1.
    - `contextLengthReached`: The context length was reached.
      This stop reason will only occur if the `context_overflow_policy`
      is set to `stopAtLimit`.
    """

    tokens_per_second: Optional[float]
    """The average number of tokens predicted per second.

    Note: This value can be None in the case of a very short prediction,
    which results in a NaN or a Infinity value.
    """

    num_gpu_layers: Optional[int]
    """The number of GPU layers used in the prediction."""

    time_to_first_token_sec: Optional[float]
    """The time it took to predict the first token in seconds."""

    prompt_tokens_count: Optional[int]
    """The number of tokens that were supplied."""

    predicted_tokens_count: Optional[int]
    """The number of tokens that were predicted."""

    total_tokens_count: Optional[int]
    """The total number of tokens. This is the sum of the prompt tokens and the predicted tokens."""

    def __init__(
        self,
        stopReason: LLMPredictionStopReason,
        tokensPerSecond: Optional[float],
        numGpuLayers: Optional[int],
        timeToFirstTokenSec: Optional[float],
        promptTokensCount: Optional[int],
        predictedTokensCount: Optional[int],
        totalTokensCount: Optional[int],
    ):
        self.stop_reason = stopReason
        self.tokens_per_second = tokensPerSecond
        self.num_gpu_layers = numGpuLayers
        self.time_to_first_token_sec = timeToFirstTokenSec
        self.prompt_tokens_count = promptTokensCount
        self.predicted_tokens_count = predictedTokensCount
        self.total_tokens_count = totalTokensCount
