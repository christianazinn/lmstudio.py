from .AsyncEmbeddingDynamicHandle import EmbeddingDynamicHandle
from .AsyncLLMDynamicHandle import LLMDynamicHandle
from ...backend_common import BaseEmbeddingSpecificModel, BaseLLMSpecificModel


"""
Weird inheritance structure:
With the way lms_common is currently implemented, SpecificModel ends up just being DynamicHandle,
so we wrap BaseSpecificModel in BaseEmbeddingSpecificModel and BaseLLMSpecificModel for typing and then
all the methods we want are conveniently inherited. /shrug
"""


class EmbeddingSpecificModel(EmbeddingDynamicHandle, BaseEmbeddingSpecificModel):
    """
    Represents a specific loaded Embedding. Most Embedding related operations are inherited from
    {@link EmbeddingDynamicHandle}.

    :public:
    """


class LLMSpecificModel(LLMDynamicHandle, BaseLLMSpecificModel):
    """
    Represents a specific loaded LLM. Most LLM related operations are inherited from
    {@link LLMDynamicHandle}.

    :public:
    """
