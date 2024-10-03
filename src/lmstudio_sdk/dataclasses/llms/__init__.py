# pylance: disable=unused-imports
# flake8: noqa: f401
# ruff: noqa: F401
"""Dataclasses representing the data structures used in the LLM API.

Classes:
    KVConfig: A key-value configuration object.
    KVConfigField: A key-value configuration field.
    KVConfigLayerName: A key-value configuration layer name.
    KVConfigStack: A key-value configuration stack.
    KVConfigStackLayer: A key-value configuration stack layer.
    LLMChatHistory: The history of a conversation as an array of messages.
    LLMChatHistoryMessage: A single message in the history.
    LLMChatHistoryMessageContent: The content of a message in the history.
    LLMChatHistoryMessageContentPart: A part of the content of a message in the history.
    LLMChatHistoryMessageContentPartImage: The image in a message in the history.
    LLMChatHistoryMessageContentPartText: The text in a message in the history.
    LLMChatHistoryRole: A role in a specific message in the history.
    LLMContext: A raw context object that can be fed into the model.
    LLMCompletionContextInput: The input context for a conversation request.
    LLMConversationContextInput: A conversation context input object.
    LLMConversationContextInputItem: A single message in the conversation context input.
    LLMPredictionStats: Statistics about a prediction.
    LLMPredictionStopReason: The reason why a prediction stopped.
    PredictionResult: Represents the result of a prediction.
"""

from .LLMChatHistory import (
    LLMChatHistory,
    LLMChatHistoryMessage,
    LLMChatHistoryMessageContent,
    LLMChatHistoryMessageContentPart,
    LLMChatHistoryMessageContentPartImage,
    LLMChatHistoryMessageContentPartText,
    LLMChatHistoryRole,
    LLMContext,
    LLMCompletionContextInput,
    LLMConversationContextInput,
    LLMConversationContextInputItem,
)
from .KVConfig import (
    convert_dict_to_kv_config,
    find_key_in_kv_config,
    KVConfig,
    KVConfigField,
    KVConfigLayerName,
    KVConfigStack,
    KVConfigStackLayer,
)
from .LLMPredictionStats import (
    dict_to_stats,
    LLMPredictionStopReason,
    LLMPredictionStats,
)
from .PredictionResult import PredictionResult

__all__ = [
    "KVConfig",
    "KVConfigField",
    "KVConfigLayerName",
    "KVConfigStack",
    "KVConfigStackLayer",
    "LLMChatHistory",
    "LLMChatHistoryMessage",
    "LLMChatHistoryMessageContent",
    "LLMChatHistoryMessageContentPart",
    "LLMChatHistoryMessageContentPartImage",
    "LLMChatHistoryMessageContentPartText",
    "LLMChatHistoryRole",
    "LLMContext",
    "LLMCompletionContextInput",
    "LLMConversationContextInput",
    "LLMConversationContextInputItem",
    "LLMPredictionStopReason",
    "LLMPredictionStats",
    "PredictionResult",
]
