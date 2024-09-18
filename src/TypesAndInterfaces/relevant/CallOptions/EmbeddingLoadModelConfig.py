from typing import Optional
from pydantic import Field
from TypesAndInterfaces.relevant.LLMGeneralSettings.LLMLlamaAccelerationSetting import LLMLlamaAccelerationSetting
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class EmbeddingLoadModelConfig(ConfiguredBaseModel):
    """
    Configuration for loading an embedding model.
    """

    gpuOffload: Optional[LLMLlamaAccelerationSetting] = Field(
        default=None, description="GPU offload settings for the model."
    )

    contextLength: Optional[int] = Field(default=None, description="The context length for the model.")

    ropeFrequencyBase: Optional[float] = Field(
        default=None, description="The base frequency for RoPE (Rotary Positional Embedding)."
    )

    ropeFrequencyScale: Optional[float] = Field(
        default=None, description="The frequency scale for RoPE (Rotary Positional Embedding)."
    )

    keepModelInMemory: Optional[bool] = Field(default=None, description="Whether to keep the model in memory.")

    tryMmap: Optional[bool] = Field(default=None, description="Whether to try memory-mapping the model.")
