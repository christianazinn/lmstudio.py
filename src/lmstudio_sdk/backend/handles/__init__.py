"""Handles and references to specific models on the server.

Classes:
    DynamicHandle: base class for dynamic handles.
    EmbeddingDynamicHandle: dynamic handle for embedding models.
    LLMDynamicHandle: dynamic handle for LLM models.
    EmbeddingSpecificModel: reference to a specific embedding model.
    LLMSpecificModel: reference to a specific LLM model.

SpecificModels are returned by `get` and `load` methods of any
`ModelNamespace`, and are used to interact with the model.
"""

from .DynamicHandle import DynamicHandle
from .EmbeddingDynamicHandle import EmbeddingDynamicHandle
from .LLMDynamicHandle import LLMDynamicHandle
from .SpecificModel import EmbeddingSpecificModel, LLMSpecificModel

__all__ = [
    "DynamicHandle",
    "EmbeddingDynamicHandle",
    "LLMDynamicHandle",
    "EmbeddingSpecificModel",
    "LLMSpecificModel",
]
