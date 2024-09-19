from typing import List, Literal, NotRequired, Union, TypedDict


LLMLlamaAccelerationOffloadRatio = Union[float, Literal["max", "off"]]
"""
How much of the model's work should be offloaded to the GPU. The value should be between 0 and 1.
A value of 0 means that no layers are offloaded to the GPU, while a value of 1 means that all
layers (that can be offloaded) are offloaded to the GPU.

This type can be:
- A float between 0 and 1
- The string "max" (representing maximum offloading)
- The string "off" (representing no offloading)
"""


class LLMLlamaAccelerationSetting(TypedDict):
    """
    Settings related to offloading work to the GPU.
    """

    ratio: LLMLlamaAccelerationOffloadRatio
    """
    The offload ratio for GPU acceleration.
    """

    mainGpu: int
    """
    The index of the main GPU to use.
    """

    tensorSplit: List[float]
    """
    The tensor split configuration for multi-GPU setups.
    """


class LLMLoadModelConfig(TypedDict):
    """
    Configuration for loading an LLM model.
    """

    gpuOffload: NotRequired[Union[LLMLlamaAccelerationSetting, float]]
    """
    How much of the model's work should be offloaded to the GPU. The value should be between 0 and 1.
    A value of 0 means that no layers are offloaded to the GPU, while a value of 1 means that all
    layers (that can be offloaded) are offloaded to the GPU.
    """

    contextLength: NotRequired[int]
    """
    The size of the context length in number of tokens. This will include both the prompts and the
    responses. Once the context length is exceeded, the value set in
    LLMPredictionConfigBase.contextOverflowPolicy is used to determine the behavior.

    See LLMContextOverflowPolicy for more information.
    """

    ropeFrequencyBase: NotRequired[float]
    ropeFrequencyScale: NotRequired[float]

    evalBatchSize: NotRequired[int]
    """
    Prompt evaluation batch size.
    """

    flashAttention: NotRequired[bool]
    keepModelInMemory: NotRequired[bool]
    seed: NotRequired[int]
    useFp16ForKVCache: NotRequired[bool]
    tryMmap: NotRequired[bool]
    numExperts: NotRequired[int]
