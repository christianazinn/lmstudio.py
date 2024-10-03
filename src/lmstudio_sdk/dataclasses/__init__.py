# pylance: disable=unused-imports
# flake8: noqa: f401
# ruff: noqa: F401
"""Dataclasses representing the data structures used in the LLM API.

Most of these are typed dicts that are used to pass data to and from the LLM API,
particularly in the case of long and repetitive argument dictionaries.

For more information, see the individual classes and submodules.
"""

from .configs import (
    BaseLoadModelOpts,
    EmbeddingLoadModelConfig,
    LLMApplyPromptTemplateOpts,
    LLMContextOverflowPolicy,
    LLMLlamaAccelerationOffloadRatio,
    LLMLlamaAccelerationSetting,
    LLMLoadModelConfig,
    LLMPredictionConfig,
    LLMPredictionExtraOpts,
    LLMPredictionOpts,
    LLMStructuredPredictionSetting,
)
from .llms import (
    convert_dict_to_kv_config,
    dict_to_stats,
    find_key_in_kv_config,
    KVConfig,
    KVConfigField,
    KVConfigLayerName,
    KVConfigStack,
    KVConfigStackLayer,
    LLMChatHistory,
    LLMChatHistoryMessage,
    LLMChatHistoryMessageContent,
    LLMChatHistoryMessageContentPart,
    LLMChatHistoryMessageContentPartImage,
    LLMChatHistoryMessageContentPartText,
    LLMChatHistoryRole,
    LLMCompletionContextInput,
    LLMContext,
    LLMConversationContextInput,
    LLMConversationContextInputItem,
    LLMPredictionStats,
    LLMPredictionStopReason,
    PredictionResult,
)
from .models import (
    DownloadedModel,
    InstanceReferenceModel,
    ModelDescriptor,
    ModelDomainType,
    ModelQuery,
    ModelSpecifier,
    QueryModel,
)

__all__ = [
    "BaseLoadModelOpts",
    "DownloadedModel",
    "EmbeddingLoadModelConfig",
    "InstanceReferenceModel",
    "KVConfig",
    "KVConfigField",
    "KVConfigLayerName",
    "KVConfigStack",
    "KVConfigStackLayer",
    "LLMApplyPromptTemplateOpts",
    "LLMChatHistory",
    "LLMChatHistoryMessage",
    "LLMChatHistoryMessageContent",
    "LLMChatHistoryMessageContentPart",
    "LLMChatHistoryMessageContentPartImage",
    "LLMChatHistoryMessageContentPartText",
    "LLMChatHistoryRole",
    "LLMCompletionContextInput",
    "LLMConversationContextInput",
    "LLMConversationContextInputItem",
    "LLMContext",
    "LLMContextOverflowPolicy",
    "LLMLlamaAccelerationOffloadRatio",
    "LLMLlamaAccelerationSetting",
    "LLMLoadModelConfig",
    "LLMPredictionConfig",
    "LLMPredictionExtraOpts",
    "LLMPredictionOpts",
    "LLMPredictionStats",
    "LLMPredictionStopReason",
    "LLMStructuredPredictionSetting",
    "ModelDescriptor",
    "ModelDomainType",
    "ModelQuery",
    "ModelSpecifier",
    "PredictionResult",
    "QueryModel",
]
