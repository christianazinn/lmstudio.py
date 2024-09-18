from typing import List, Union, Literal, TypedDict

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
