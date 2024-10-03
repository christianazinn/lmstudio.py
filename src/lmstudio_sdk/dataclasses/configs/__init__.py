"""Configuration dict dataclasses for various operations.

Classes:
    BaseLoadModelOpts: Base options for loading a model.
    EmbeddingLoadModelConfig: Configuration for loading an embedding model.
    LLMApplyPromptTemplateOpts: Options for applying a prompt template.
    LLMContextOverflowPolicy: Behavior when the generated tokens length exceeds the context window size.
    LLMLlamaAccelerationSetting: Settings related to offloading work to the GPU.
    LLMLlamaAccelerationOffloadRatio: How much of the model's work should be offloaded to the GPU.
    LLMLoadModelConfig: Configuration for loading an LLM model.
    LLMPredictionConfig: Shared config for running predictions on an LLM.
    LLMPredictionExtraOpts: Internal options for prediction that are not passed to the server.
    LLMPredictionOpts: Shared options for any prediction methods.
    LLMStructuredPredictionSetting: Structured prediction settings for an LLM model.
"""

from .BaseLoadModelOpts import BaseLoadModelOpts
from .EmbeddingLoadModelConfig import EmbeddingLoadModelConfig
from .LLMApplyPromptTemplateOpts import LLMApplyPromptTemplateOpts
from .LLMLoadModelConfig import (
    LLMLlamaAccelerationSetting,
    LLMLlamaAccelerationOffloadRatio,
    LLMLoadModelConfig,
)
from .LLMPredictionOpts import (
    LLMContextOverflowPolicy,
    LLMPredictionConfig,
    LLMPredictionExtraOpts,
    LLMPredictionOpts,
)
from .LLMStructuredPredictionSetting import LLMStructuredPredictionSetting

__all__ = [
    "BaseLoadModelOpts",
    "EmbeddingLoadModelConfig",
    "LLMApplyPromptTemplateOpts",
    "LLMContextOverflowPolicy",
    "LLMLlamaAccelerationSetting",
    "LLMLlamaAccelerationOffloadRatio",
    "LLMLoadModelConfig",
    "LLMPredictionConfig",
    "LLMPredictionExtraOpts",
    "LLMPredictionOpts",
    "LLMStructuredPredictionSetting",
]
