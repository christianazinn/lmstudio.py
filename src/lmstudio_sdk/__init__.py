"""The Python SDK for the LM Studio WebSocket API.

Use this SDK to interact with the LM Studio server using Python.
It provides a strict superset of whatever you could do with
calling the HTTP OpenAI-like API with the OpenAI Python SDK,
and is intended to be a near drop-in replacement.

It also provides feature parity with the TypeScript SDK, so any
code you have in TypeScript can be translated almost directly
to Python.

Please refer to the README on the official project GitHub
for examples and documentation.
"""
# TODO: make a better and longer docstring

from .backend import (
    AsyncLMStudioClient,
    AsyncOngoingPrediction,
    DiagnosticsNamespace,
    DynamicHandle,
    EmbeddingDynamicHandle,
    EmbeddingNamespace,
    EmbeddingSpecificModel,
    LLMDynamicHandle,
    LLMNamespace,
    LLMSpecificModel,
    LMStudioClient,
    ModelNamespace,
    SyncOngoingPrediction,
    SyncLMStudioClient,
)
from .dataclasses import (
    BaseLoadModelOpts,
    DownloadedModel,
    EmbeddingLoadModelConfig,
    InstanceReferenceModel,
    KVConfig,
    KVConfigField,
    KVConfigLayerName,
    KVConfigStack,
    KVConfigStackLayer,
    LLMApplyPromptTemplateOpts,
    LLMChatHistory,
    LLMChatHistoryMessage,
    LLMChatHistoryMessageContent,
    LLMChatHistoryMessageContentPart,
    LLMChatHistoryMessageContentPartImage,
    LLMChatHistoryMessageContentPartText,
    LLMChatHistoryRole,
    LLMCompletionContextInput,
    LLMConversationContextInput,
    LLMConversationContextInputItem,
    LLMContext,
    LLMContextOverflowPolicy,
    LLMLlamaAccelerationOffloadRatio,
    LLMLlamaAccelerationSetting,
    LLMLoadModelConfig,
    LLMPredictionConfig,
    LLMPredictionExtraOpts,
    LLMPredictionOpts,
    LLMPredictionStats,
    LLMPredictionStopReason,
    LLMStructuredPredictionSetting,
    ModelDescriptor,
    ModelDomainType,
    ModelQuery,
    ModelSpecifier,
    PredictionResult,
    QueryModel,
)
from .utils import (
    AsyncAbortSignal,
    ChannelError,
    get_logger,
    RECV,
    RPCError,
    SEND,
    SyncAbortSignal,
    WEBSOCKET,
)

logger = get_logger(__name__)
"""
The logger for the lmstudio_sdk package.
"""

__all__ = [
    "AsyncAbortSignal",
    "AsyncLMStudioClient",
    "AsyncOngoingPrediction",
    "BaseLoadModelOpts",
    "ChannelError",
    "DiagnosticsNamespace",
    "DownloadedModel",
    "DynamicHandle",
    "EmbeddingDynamicHandle",
    "EmbeddingLoadModelConfig",
    "EmbeddingNamespace",
    "EmbeddingSpecificModel",
    "get_logger",
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
    "LLMContext",
    "LLMContextOverflowPolicy",
    "LLMConversationContextInput",
    "LLMConversationContextInputItem",
    "LLMDynamicHandle",
    "LLMLlamaAccelerationOffloadRatio",
    "LLMLlamaAccelerationSetting",
    "LLMLoadModelConfig",
    "LLMNamespace",
    "LLMPredictionConfig",
    "LLMPredictionExtraOpts",
    "LLMPredictionOpts",
    "LLMPredictionStats",
    "LLMPredictionStopReason",
    "LLMSpecificModel",
    "LLMStructuredPredictionSetting",
    "LMStudioClient",
    "ModelDescriptor",
    "ModelDomainType",
    "ModelNamespace",
    "ModelQuery",
    "ModelSpecifier",
    "PredictionResult",
    "QueryModel",
    "RECV",
    "RPCError",
    "SEND",
    "SyncAbortSignal",
    "SyncLMStudioClient",
    "SyncOngoingPrediction",
    "WEBSOCKET",
]
