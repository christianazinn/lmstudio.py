from typing import NotRequired, TypedDict

from .LLMLoadModelConfig import LLMLlamaAccelerationSetting


class EmbeddingLoadModelConfig(TypedDict):
    # TODO: docstring
    """
    Configuration for loading an embedding model.
    """

    gpu_offload: NotRequired[LLMLlamaAccelerationSetting]
    """
    GPU offload settings for the model.
    """

    context_length: NotRequired[int]
    """
    The context length to use for the model.
    """

    rope_frequency_base: NotRequired[float]
    """
    The base frequency for RoPE (Rotary Positional Embedding).
    """

    rope_frequency_scale: NotRequired[float]
    """
    The frequency scale for RoPE (Rotary Positional Embedding).
    """

    keep_model_in_memory: NotRequired[bool]
    """
    Whether to keep the model in memory.
    """

    try_mmap: NotRequired[bool]
    """
    Whether to try memory-mapping the model.
    """
