from typing import TypedDict
from TypesAndInterfaces.relevant.Predictions.LLMPredictionStats import LLMPredictionStats
from TypesAndInterfaces.relevant.ModelDescriptors.ModelDescriptor import ModelDescriptor
from TypesAndInterfaces.relevant.LLMGeneralSettings.KVConfig import KVConfig


class PredictionResult(TypedDict):
    """
    Represents the result of a prediction.

    The most notable property is `content`, which contains the generated text.
    Additionally, the `stats` property contains statistics about the prediction.
    """

    content: str
    """The newly generated text as predicted by the LLM."""

    stats: LLMPredictionStats
    """Statistics about the prediction."""

    model_info: ModelDescriptor
    """Information about the model used for the prediction."""

    load_config: KVConfig
    """The configuration used to load the model."""

    prediction_config: KVConfig
    """The configuration used for the prediction."""
