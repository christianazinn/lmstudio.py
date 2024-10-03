import lmstudio_sdk.dataclasses as dc
import lmstudio_sdk.backend.communications as comms

from .DynamicHandle import DynamicHandle
from .EmbeddingDynamicHandle import EmbeddingDynamicHandle
from .LLMDynamicHandle import LLMDynamicHandle


class SpecificModel(DynamicHandle):
    """Represents a specific model on the remote server.

    Retains a reference to the specific instance reference of the model.
    """

    identifier: str

    def __init__(
        self,
        port: comms.BaseClientPort,
        instance_reference: str,
        descriptor: dc.ModelDescriptor,
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
    """Represents a specific loaded embedding model.

    Embedding related operations are inherited from EmbeddingDynamicHandle.
    """


class LLMSpecificModel(LLMDynamicHandle, SpecificModel):
    """Represents a specific loaded LLM.

    LLM related operations are inherited from LLMDynamicHandle.
    """
