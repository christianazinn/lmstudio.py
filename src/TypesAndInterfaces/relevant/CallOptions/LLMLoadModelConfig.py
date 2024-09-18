from typing import NotRequired, Union, TypedDict
from TypesAndInterfaces.relevant.LLMGeneralSettings.LLMLlamaAccelerationSetting import LLMLlamaAccelerationSetting


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
