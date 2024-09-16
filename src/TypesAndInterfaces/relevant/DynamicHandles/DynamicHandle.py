from typing import Optional
from Defaults.ConfiguredBaseModel import ConfiguredBaseModel
from Defaults.ClientPort import ClientPort
from ModelDescriptors.ModelDescriptor import ModelDescriptor
from ModelDescriptors.ModelSpecifier import ModelSpecifier
from LLMGeneralSettings.KVConfig import KVConfig
# TODO every kind of validation


class DynamicHandle(ConfiguredBaseModel):
    port: ClientPort
    specifier: ModelSpecifier

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
        return info["descriptor"]

    async def get_load_config(self) -> KVConfig:
        load_config = await self.port.callRpc("getLoadConfig", {"specifier": self.specifier})
        return load_config


# Note: The `get_current_stack` function is not provided in the original TypeScript code.
# You might need to implement this function separately or import it from the appropriate module.
def get_current_stack(depth: int) -> str:
    # Implementation of get_current_stack goes here
    pass
