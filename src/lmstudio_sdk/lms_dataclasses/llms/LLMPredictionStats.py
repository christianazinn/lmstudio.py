from enum import Enum
from typing import NotRequired, TypedDict


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
      with the `stop_strings` config option. This stop reason will only occur if the `stop_strings`
      config option is set to an array of strings.)
    - `maxPredictedTokensReached`: The maximum number of tokens to predict was reached. (Length limit
      can be specified with the `maxPredictedTokens` config option. This stop reason will only occur
      if the `maxPredictedTokens` config option is set to a value other than -1.)
    - `contextLengthReached`: The context length was reached. This stop reason will only occur if the
      `context_overflow_policy` is set to `stopAtLimit`.
    """

    USER_STOPPED = "userStopped"
    MODEL_UNLOADED = "modelUnloaded"
    FAILED = "failed"
    EOS_FOUND = "eosFound"
    STOP_STRING_FOUND = "stopStringFound"
    MAX_PREDICTED_TOKENS_REACHED = "maxPredictedTokensReached"
    CONTEXT_LENGTH_REACHED = "contextLengthReached"


class LLMPredictionStats(TypedDict):
    """
    @public
    """

    stop_reason: LLMPredictionStopReason
    """
    The reason why the prediction stopped.

    This is a string enum with the following possible values:

    - `userStopped`: The user stopped the prediction. This includes calling the `cancel` method on
      the `OngoingPrediction` object.
    - `modelUnloaded`: The model was unloaded during the prediction.
    - `failed`: An error occurred during the prediction.
    - `eosFound`: The model predicted an end-of-sequence token, which is a way for the model to
      indicate that it "thinks" the sequence is complete.
    - `stopStringFound`: A stop string was found in the prediction. (Stop strings can be specified
      with the `stop_strings` config option. This stop reason will only occur if the `stop_strings`
      config option is set.)
    - `maxPredictedTokensReached`: The maximum number of tokens to predict was reached. (Length
      limit can be specified with the `maxPredictedTokens` config option. This stop reason will
      only occur if the `maxPredictedTokens` config option is set to a value other than -1.)
    - `contextLengthReached`: The context length was reached. This stop reason will only occur if
      the `context_overflow_policy` is set to `stopAtLimit`.
    """

    tokens_per_second: NotRequired[float]
    """
    The average number of tokens predicted per second.

    Note: This value can be None in the case of a very short prediction which results in a
    NaN or a Infinity value.
    """

    num_gpu_layers: NotRequired[int]
    """
    The number of GPU layers used in the prediction.
    """

    time_to_first_token_sec: NotRequired[float]
    """
    The time it took to predict the first token in seconds.
    """

    prompt_tokens_count: NotRequired[int]
    """
    The number of tokens that were supplied.
    """

    predicted_tokens_count: NotRequired[int]
    """
    The number of tokens that were predicted.
    """

    total_tokens_count: NotRequired[int]
    """
    The total number of tokens. This is the sum of the prompt tokens and the predicted tokens.
    """
