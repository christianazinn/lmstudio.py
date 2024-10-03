"""Namespaces for top-level server functions.

Classes:
    DiagnosticsNamespace: Method namespace for server diagnostics.
    EmbeddingNamespace: Method namespace for embedding functions.
    LLMNamespace: Method namespace for LLM functions.
    SystemNamespace: Method namespace for LM Studio system functions.
"""

from .DiagnosticsNamespace import DiagnosticsNamespace
from .ModelNamespace import EmbeddingNamespace, LLMNamespace
from .SystemNamespace import SystemNamespace

__all__ = [
    "LLMNamespace",
    "EmbeddingNamespace",
    "SystemNamespace",
    "DiagnosticsNamespace",
]
