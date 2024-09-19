from ...lms_dataclasses import ModelDescriptor
from ..communications import ClientPort
from .DynamicHandle import DynamicHandle
from .EmbeddingDynamicHandle import EmbeddingDynamicHandle
from .LLMDynamicHandle import LLMDynamicHandle


class SpecificModel(DynamicHandle):
    identifier: str
    specifier: str


class EmbeddingSpecificModel(EmbeddingDynamicHandle, SpecificModel):
    """
    Represents a specific loaded Embedding. Most Embedding related operations are inherited from
    {@link EmbeddingDynamicHandle}.

    :public:
    """

    def __init__(self, port: ClientPort, instance_reference: str, descriptor: ModelDescriptor):
        assert isinstance(port, ClientPort)
        assert isinstance(instance_reference, str)
        EmbeddingDynamicHandle.__init__(
            self, port, {"type": "instanceReference", "instanceReference": instance_reference}
        )
        self.identifier = descriptor["identifier"]
        self.path = descriptor["path"]


class LLMSpecificModel(LLMDynamicHandle, SpecificModel):
    """
    Represents a specific loaded LLM. Most LLM related operations are inherited from
    {@link LLMDynamicHandle}.

    :public:
    """

    def __init__(self, port: ClientPort, instance_reference: str, descriptor: ModelDescriptor):
        assert isinstance(port, ClientPort)
        assert isinstance(instance_reference, str)
        super().__init__(port=port, specifier={"type": "instanceReference", "instanceReference": instance_reference})
        self.identifier = descriptor["identifier"]
        self.path = descriptor["path"]
