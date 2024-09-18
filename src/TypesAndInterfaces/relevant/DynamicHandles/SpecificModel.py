from TypesAndInterfaces.relevant.DynamicHandles.DynamicHandle import DynamicHandle
from TypesAndInterfaces.relevant.DynamicHandles.EmbeddingDynamicHandle import EmbeddingDynamicHandle
from TypesAndInterfaces.relevant.DynamicHandles.LLMDynamicHandle import LLMDynamicHandle
from TypesAndInterfaces.relevant.Defaults.ClientPort import ClientPort
from TypesAndInterfaces.relevant.ModelDescriptors.ModelDescriptor import ModelDescriptor


class SpecificModel(DynamicHandle):
    identifier: str
    specifier: str

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        extra = "forbid"


class EmbeddingSpecificModel(EmbeddingDynamicHandle, SpecificModel):
    """
    Represents a specific loaded Embedding. Most Embedding related operations are inherited from
    {@link EmbeddingDynamicHandle}.

    :public:
    """

    def __init__(self, port: ClientPort, instance_reference: str, descriptor: ModelDescriptor):
        assert isinstance(port, ClientPort)
        assert isinstance(instance_reference, str)
        descriptor = ModelDescriptor.model_validate(descriptor)
        EmbeddingDynamicHandle.__init__(
            self, port, {"type": "instanceReference", "instanceReference": instance_reference}
        )
        self.identifier = descriptor.identifier
        self.path = descriptor.path


class LLMSpecificModel(LLMDynamicHandle, SpecificModel):
    """
    Represents a specific loaded LLM. Most LLM related operations are inherited from
    {@link LLMDynamicHandle}.

    :public:
    """

    def __init__(self, port: ClientPort, instance_reference: str, descriptor: ModelDescriptor):
        assert isinstance(port, ClientPort)
        assert isinstance(instance_reference, str)
        descriptor = ModelDescriptor.model_validate(descriptor)
        LLMDynamicHandle.__init__(self, port, {"type": "instanceReference", "instanceReference": instance_reference})
        self.identifier = descriptor.identifier
        self.path = descriptor.path
