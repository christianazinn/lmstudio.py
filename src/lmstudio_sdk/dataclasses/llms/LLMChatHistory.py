from typing import List, Literal, TypedDict, Union


LLMChatHistoryMessageContent = List["LLMChatHistoryMessageContentPart"]
"""Represents the content of a message in the history."""


class LLMChatHistoryMessageContentPartText(TypedDict):
    """Represents a text in a message in the history."""

    type: Literal["text"]
    text: str


class LLMChatHistoryMessageContentPartImage(TypedDict):
    """Represents an image in a message in the history."""

    type: Literal["imageBase64"]
    base64: str


LLMChatHistoryMessageContentPart = Union[
    LLMChatHistoryMessageContentPartText, LLMChatHistoryMessageContentPartImage
]
"""Represents a part of the content of a message in the history."""

LLMChatHistoryRole = Literal["system", "user", "assistant"]
"""Represents a role in a specific message in the history.

This is a string enum, and can only be one of the following values:

- `system`: Usually used for system prompts
- `user`: Used for user inputs / queries
- `assistant`: Used for assistant responses,
               usually generated AI, but can also be fed by a human
"""


class LLMChatHistoryMessage(TypedDict):
    """Represents a single message in the history."""

    role: LLMChatHistoryRole
    content: LLMChatHistoryMessageContent


LLMChatHistory = List[LLMChatHistoryMessage]
"""Represents the history of a conversation as an array of messages."""


class LLMContext(TypedDict):
    """Represents a raw context object that can be fed into the model."""

    history: LLMChatHistory


LLMCompletionContextInput = str
"""Represents the input context for a completion request."""


class LLMConversationContextInputItem(TypedDict):
    """Represents a single message in the conversation context input."""

    role: LLMChatHistoryRole
    content: str


LLMConversationContextInput = List[LLMConversationContextInputItem]
"""Represents the input context for a conversation request."""
