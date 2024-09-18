from typing import Optional, Union
from pydantic import Field
from TypesAndInterfaces.relevant.LLMGeneralSettings.LLMLlamaAccelerationSetting import LLMLlamaAccelerationSetting
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class LLMLoadModelConfig(ConfiguredBaseModel):
    """
    Configuration for loading an LLM model.
    """

    gpuOffload: Optional[Union[LLMLlamaAccelerationSetting, float, str]] = Field(
        default=None,
        description="""
    How much of the model's work should be offloaded to the GPU. The value should be between 0 and 1.
    A value of 0 means that no layers are offloaded to the GPU, while a value of 1 means that all
    layers (that can be offloaded) are offloaded to the GPU.

    Alternatively, the value can be set to "auto", which means it will be determined automatically.
    (Currently uses the value in the preset.)
    """,
    )

    contextLength: Optional[int] = Field(
        default=None,
        description="""
    The size of the context length in number of tokens. This will include both the prompts and the
    responses. Once the context length is exceeded, the value set in
    LLMPredictionConfigBase.contextOverflowPolicy is used to determine the behavior.

    See LLMContextOverflowPolicy for more information.
    """,
    )

    ropeFrequencyBase: Optional[float] = None
    ropeFrequencyScale: Optional[float] = None

    evalBatchSize: Optional[int] = Field(default=None, description="Prompt evaluation batch size.")

    flashAttention: Optional[bool] = None
    keepModelInMemory: Optional[bool] = None
    seed: Optional[int] = None
    useFp16ForKVCache: Optional[bool] = None
    tryMmap: Optional[bool] = None
    numExperts: Optional[int] = None
