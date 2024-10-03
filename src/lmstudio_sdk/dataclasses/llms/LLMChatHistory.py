from typing import List, Literal, TypedDict, Union


LLMChatHistoryMessageContent = List["LLMChatHistoryMessageContentPart"]
"""The content of a message in the history."""


class LLMChatHistoryMessageContentPartText(TypedDict):
    """The text in a message in the history."""

    type: Literal["text"]
    text: str


class LLMChatHistoryMessageContentPartImage(TypedDict):
    """The image in a message in the history."""

    type: Literal["imageBase64"]
    base64: str


LLMChatHistoryMessageContentPart = Union[
    LLMChatHistoryMessageContentPartText, LLMChatHistoryMessageContentPartImage
]
"""A part of the content of a message in the history."""

LLMChatHistoryRole = Literal["system", "user", "assistant"]
"""A role in a specific message in the history.

This is a string enum, and can only be one of the following values:

- `system`: Usually used for system prompts
- `user`: Used for user inputs / queries
- `assistant`: Used for assistant responses,
               usually generated AI, but can also be fed by a human
"""


class LLMChatHistoryMessage(TypedDict):
    """A single message in the history."""

    role: LLMChatHistoryRole
    content: LLMChatHistoryMessageContent


LLMChatHistory = List[LLMChatHistoryMessage]
"""The history of a conversation as an array of messages."""


class LLMContext(TypedDict):
    """A raw context object that can be fed into the model."""

    history: LLMChatHistory


LLMCompletionContextInput = str
"""The input context for a completion request."""


class LLMConversationContextInputItem(TypedDict):
    """A single message in the conversation context input."""

    role: LLMChatHistoryRole
    content: str


LLMConversationContextInput = List[LLMConversationContextInputItem]
"""The input context for a conversation request."""
