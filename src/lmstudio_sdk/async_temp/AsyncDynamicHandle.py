from typing import Optional
from ..communications import ClientPort
from ...lms_dataclasses import ModelDescriptor, ModelSpecifier, KVConfig


class DynamicHandle:
    """
    This represents a set of requirements for a model. It is not tied to a specific model, but rather
    to a set of requirements that a model must satisfy.

    For example, if you got the model via `client.llm.get("my-identifier")`, you will get a
    `LLMModel` for the model with the identifier `my-identifier`. If the model is unloaded, and
    another model is loaded with the same identifier, using the same `LLMModel` will use the new
    model.
    """

    port: ClientPort
    specifier: ModelSpecifier

    def __init__(self, port: ClientPort, specifier: ModelSpecifier):
        self.port = port
        self.specifier = specifier

    async def get_model_info(self) -> Optional[ModelDescriptor]:
        """
        Gets the information of the model that is currently associated with this `LLMModel`. If no
        model is currently associated, this will return `None`.

        Note: As models are loaded/unloaded, the model associated with this `LLMModel` may change at
        any moment.
        """
        info = await self.port.call_rpc("getModelInfo", {"specifier": self.specifier, "throwIfNotFound": False})
        if info is None:
            return None
        return info.get("descriptor", None)

    async def get_load_config(self) -> KVConfig:
        return await self.port.call_rpc("getLoadConfig", {"specifier": self.specifier})
