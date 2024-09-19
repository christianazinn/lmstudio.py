from typing import NotRequired, TypedDict
from .LLMLoadModelConfig import LLMLlamaAccelerationSetting


class EmbeddingLoadModelConfig(TypedDict):
    """
    Configuration for loading an embedding model.
    """

    gpuOffload: NotRequired[LLMLlamaAccelerationSetting]
    """
    GPU offload settings for the model.
    """

    contextLength: NotRequired[int]
    """
    The context length to use for the model.
    """

    ropeFrequencyBase: NotRequired[float]
    """
    The base frequency for RoPE (Rotary Positional Embedding).
    """

    ropeFrequencyScale: NotRequired[float]
    """
    The frequency scale for RoPE (Rotary Positional Embedding).
    """

    keepModelInMemory: NotRequired[bool]
    """
    Whether to keep the model in memory.
    """

    tryMmap: NotRequired[bool]
    """
    Whether to try memory-mapping the model.
    """
