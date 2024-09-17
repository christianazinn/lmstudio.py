from typing import List, Any
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel
from enum import Enum, auto


class KVConfigField(ConfiguredBaseModel):
    key: str
    value: Any = None


class KVConfig(ConfiguredBaseModel):
    fields: List[KVConfigField]

    @staticmethod
    def convert_dict_to_kv_config(kv_dict: dict):
        return KVConfig(fields=[KVConfigField(key=k, value=v) for k, v in kv_dict.items()])


class KVConfigLayerName(Enum):
    # Config that is currently loaded by the model
    CURRENTLY_LOADED = auto()

    # Override provided by the caller of the API
    API_OVERRIDE = auto()

    # Chat specific config in chats
    CONVERSATION_SPECIFIC = auto()

    # Cross-chat global config in chats
    CONVERSATION_GLOBAL = auto()

    # Override provided in the OpenAI http server
    HTTP_SERVER_REQUEST_OVERRIDE = auto()

    # Override to allow complete mode formatting
    COMPLETE_MODE_FORMATTING = auto()

    # Instance specific config (set in the server tab)
    INSTANCE = auto()

    # User editable per model defaults
    USER_MODEL_DEFAULT = auto()

    # Virtual model baked in configs
    VIRTUAL_MODEL = auto()

    # LM Studio provided per model defaults
    MODEL_DEFAULT = auto()


class KVConfigStackLayer(ConfiguredBaseModel):
    layerName: KVConfigLayerName
    config: KVConfig


class KVConfigStack(ConfiguredBaseModel):
    layers: List[KVConfigStackLayer]
