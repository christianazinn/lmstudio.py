from typing import List, Literal, NotRequired, TypedDict, Union


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

    main_gpu: int
    """
    The index of the main GPU to use.
    """

    tensor_split: List[float]
    """
    The tensor split configuration for multi-GPU setups.
    """


class LLMLoadModelConfig(TypedDict):
    """
    Configuration for loading an LLM model.
    """

    gpu_offload: NotRequired[Union[LLMLlamaAccelerationSetting, float]]
    """
    How much of the model's work should be offloaded to the GPU. The value should be between 0 and 1.
    A value of 0 means that no layers are offloaded to the GPU, while a value of 1 means that all
    layers (that can be offloaded) are offloaded to the GPU.
    """

    context_length: NotRequired[int]
    """
    The size of the context length in number of tokens. This will include both the prompts and the
    responses. Once the context length is exceeded, the value set in
    LLMPredictionConfigBase.context_overflow_policy is used to determine the behavior.

    See LLMContextOverflowPolicy for more information.
    """

    rope_frequency_base: NotRequired[float]
    rope_frequency_scale: NotRequired[float]

    eval_batch_size: NotRequired[int]
    """
    Prompt evaluation batch size.
    """

    flash_attention: NotRequired[bool]
    keep_model_in_memory: NotRequired[bool]
    seed: NotRequired[int]
    use_fp16_for_kv_cache: NotRequired[bool]
    try_mmap: NotRequired[bool]
    num_experts: NotRequired[int]
