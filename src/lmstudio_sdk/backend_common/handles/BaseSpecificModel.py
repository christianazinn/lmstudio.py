from abc import ABC

from ..communications import BaseClientPort
from .BaseDynamicHandle import BaseDynamicHandle

from ...lms_dataclasses import ModelDescriptor


class BaseSpecificModel(BaseDynamicHandle, ABC):
    identifier: str
    specifier: str

    def __init__(self, port: BaseClientPort, instance_reference: str, descriptor: ModelDescriptor):
        assert isinstance(port, BaseClientPort)
        assert isinstance(instance_reference, str)
        super().__init__(port, {"type": "instanceReference", "instanceReference": instance_reference})
        self.identifier = descriptor["identifier"]
        self.path = descriptor["path"]


class BaseEmbeddingSpecificModel(BaseSpecificModel):
    pass


class BaseLLMSpecificModel(BaseSpecificModel):
    pass
