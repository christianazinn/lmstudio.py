"""Backend and communication classes for the LM Studio SDK.

Classes:
    AsyncLMStudioClient: asynchronous client using asyncio.
    SyncLMStudioClient: synchronous client using blocking calls.
    AsyncOngoingPrediction: ongoing prediction for asynchronous clients.
    SyncOngoingPrediction: ongoing prediction for synchronous clients.
    DynamicHandle: base class for dynamic handles.
    EmbeddingDynamicHandle: dynamic handle for embedding functions.
    EmbeddingSpecificModel: specific model for embedding functions.
    LLMDynamicHandle: dynamic handle for LLM functions.
    LLMSpecificModel: specific model for LLM functions.
    DiagnosticsNamespace: method namespace for server diagnostics.
    EmbeddingNamespace: method namespace for embedding functions.
    LLMNamespace: method namespace for LLM functions.
    ModelNamespace: method namespace for model functions.
"""

from .client import AsyncLMStudioClient, LMStudioClient, SyncLMStudioClient
from .communications import (
    AsyncOngoingPrediction,
    SyncOngoingPrediction,
)
from .handles import (
    DynamicHandle,
    EmbeddingDynamicHandle,
    EmbeddingSpecificModel,
    LLMDynamicHandle,
    LLMSpecificModel,
)
from .namespaces import (
    DiagnosticsNamespace,
    EmbeddingNamespace,
    LLMNamespace,
    ModelNamespace,
)

__all__ = [
    "AsyncLMStudioClient",
    "AsyncOngoingPrediction",
    "DiagnosticsNamespace",
    "DynamicHandle",
    "EmbeddingDynamicHandle",
    "EmbeddingNamespace",
    "EmbeddingSpecificModel",
    "LLMDynamicHandle",
    "LLMNamespace",
    "LLMSpecificModel",
    "LMStudioClient",
    "ModelNamespace",
    "SyncOngoingPrediction",
    "SyncLMStudioClient",
]
