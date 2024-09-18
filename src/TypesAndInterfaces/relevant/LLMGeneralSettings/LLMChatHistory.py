from typing import List, Union, Literal
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel

LLMChatHistoryMessageContent = List["LLMChatHistoryMessageContentPart"]
"""Represents the content of a message in the history."""


class LLMChatHistoryMessageContentPartText(ConfiguredBaseModel):
    type: Literal["text"] = "text"
    text: str


class LLMChatHistoryMessageContentPartImage(ConfiguredBaseModel):
    type: Literal["imageBase64"] = "imageBase64"
    base64: str


LLMChatHistoryMessageContentPart = Union[LLMChatHistoryMessageContentPartText, LLMChatHistoryMessageContentPartImage]
"""Represents a part of the content of a message in the history."""

LLMChatHistoryRole = Literal["system", "user", "assistant"]
"""
Represents a role in a specific message in the history. This is a string enum, and can only be one of the following values:

- `system`: Usually used for system prompts
- `user`: Used for user inputs / queries
- `assistant`: Used for assistant responses, usually generated AI, but can also be fed by a human
"""


class LLMChatHistoryMessage(ConfiguredBaseModel):
    """
    Represents a single message in the history.
    """

    role: LLMChatHistoryRole
    content: LLMChatHistoryMessageContent


LLMChatHistory = List[LLMChatHistoryMessage]
"""Represents the history of a conversation, which is represented as an array of messages."""


class LLMContext(ConfiguredBaseModel):
    """
    Represents a raw context object that can be fed into the model.
    """

    history: LLMChatHistory


LLMCompletionContextInput = str
"""Represents the input context for a completion request. This is a string that represents the entire conversation history."""

LLMContextOverflowPolicy = Literal["stopAtLimit", "truncateMiddle", "rollingWindow"]
"""
Behavior for when the generated tokens length exceeds the context window size. Only the following values are allowed:

- `stopAtLimit`: Stop the prediction when the generated tokens length exceeds the context window
  size. If the generation is stopped because of this limit, the `stopReason` in the prediction
  stats will be set to `contextLengthReached`.
- `truncateMiddle`: Keep the system prompt and the first user message, truncate middle.
- `rollingWindow`: Maintain a rolling window and truncate past messages.
"""


class LLMConversationContextInputItem(ConfiguredBaseModel):
    role: LLMChatHistoryRole
    content: str


LLMConversationContextInput = List[LLMConversationContextInputItem]
"""
Represents the input context for a conversation request. This is an array of objects, where each object represents a
single message in the conversation.
"""
