from ...dataclasses import ModelDescriptor
from ..communications import BaseClientPort
from .DynamicHandle import DynamicHandle
from .EmbeddingDynamicHandle import EmbeddingDynamicHandle
from .LLMDynamicHandle import LLMDynamicHandle


"""
Weird inheritance structure:
With the way common is currently implemented, SpecificModel ends up just being DynamicHandle,
so we wrap BaseSpecificModel in BaseEmbeddingSpecificModel and BaseLLMSpecificModel for typing and then
all the methods we want are conveniently inherited. /shrug
"""


class SpecificModel(DynamicHandle):
    identifier: str
    specifier: str

    def __init__(
        self,
        port: BaseClientPort,
        instance_reference: str,
        descriptor: ModelDescriptor,
    ):
        assert isinstance(instance_reference, str)
        super().__init__(
            port,
            {
                "type": "instanceReference",
                "instanceReference": instance_reference,
            },
        )
        self.identifier = descriptor["identifier"]
        self.path = descriptor["path"]


class EmbeddingSpecificModel(EmbeddingDynamicHandle, SpecificModel):
    """
    Represents a specific loaded Embedding. Most Embedding related operations are inherited from
    {@link EmbeddingDynamicHandle}.

    :public:
    """


class LLMSpecificModel(LLMDynamicHandle, SpecificModel):
    """
    Represents a specific loaded LLM. Most LLM related operations are inherited from
    {@link LLMDynamicHandle}.

    :public:
    """
