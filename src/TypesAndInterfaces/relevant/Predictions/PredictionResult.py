from Defaults.ConfiguredBaseModel import ConfiguredBaseModel
from pydantic import Field
from LLMPredictionStats import LLMPredictionStats
from ModelDescriptors.ModelDescriptor import ModelDescriptor
from LLMGeneralSettings.KVConfig import KVConfig


class PredictionResult(ConfiguredBaseModel):
    """
    Represents the result of a prediction.

    The most notable property is `content`, which contains the generated text.
    Additionally, the `stats` property contains statistics about the prediction.
    """

    content: str = Field(..., description="The newly generated text as predicted by the LLM.")
    stats: LLMPredictionStats = Field(..., description="Statistics about the prediction.")
    model_info: ModelDescriptor = Field(..., description="Information about the model used for the prediction.")
    load_config: KVConfig = Field(..., description="The configuration used to load the model.")
    prediction_config: KVConfig = Field(..., description="The configuration used for the prediction.")

    class Config:
        allow_population_by_field_name = True
