import lmstudio_sdk.dataclasses.models as models

from .KVConfig import KVConfig
from .LLMPredictionStats import LLMPredictionStats


class PredictionResult:
    """Represents the result of a prediction.

    The most notable property is `content`,
    which contains the generated text.
    Additionally, the `stats` property
    contains statistics about the prediction.
    """

    content: str
    """The newly generated text as predicted by the LLM."""

    stats: LLMPredictionStats
    """Statistics about the prediction."""

    model_info: models.ModelDescriptor
    """Information about the model used for the prediction."""

    load_config: KVConfig
    """The configuration used to load the model."""

    prediction_config: KVConfig
    """The configuration used for the prediction."""

    def __init__(
        self,
        content: str,
        stats: LLMPredictionStats,
        model_info: models.ModelDescriptor,
        load_config: KVConfig,
        prediction_config: KVConfig,
    ):
        self.content = content
        self.stats = stats
        self.model_info = model_info
        self.load_config = load_config
        self.prediction_config = prediction_config
