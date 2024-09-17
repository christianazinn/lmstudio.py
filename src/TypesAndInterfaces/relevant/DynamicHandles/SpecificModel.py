from DynamicHandles.DynamicHandle import DynamicHandle
from DynamicHandles.EmbeddingDynamicHandle import EmbeddingDynamicHandle
from DynamicHandles.LLMDynamicHandle import LLMDynamicHandle


class SpecificModel(DynamicHandle):
    identifier: str
    specifier: str

    # readonly
    class Config:
        frozen = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        extra = "forbid"

    def __init__(self, identifier: str, path: str, **data):
        super().__init__(**data)
        object.__setattr__(self, 'identifier', identifier)
        object.__setattr__(self, 'path', path)


class EmbeddingSpecificModel(EmbeddingDynamicHandle, SpecificModel):
    """
    Represents a specific loaded Embedding. Most Embedding related operations are inherited from
    {@link EmbeddingDynamicHandle}.

    :public:
    """
    pass


class LLMSpecificModel(LLMDynamicHandle, SpecificModel):
    """
    Represents a specific loaded LLM. Most LLM related operations are inherited from
    {@link LLMDynamicHandle}.

    :public:
    """
    pass
