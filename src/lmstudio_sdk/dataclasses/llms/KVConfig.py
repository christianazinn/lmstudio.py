import enum
from typing import Any, List, TypedDict


class KVConfigField(TypedDict):
    """Represents a key-value configuration field."""
    key: str
    value: Any


class KVConfig(TypedDict):
    """Represents a key-value configuration object."""
    fields: List[KVConfigField]


def convert_dict_to_kv_config(kv_dict: dict) -> KVConfig:
    return {
        "fields": [
            KVConfigField(key=k, value=v)
            for k, v in kv_dict.items()
            if v and v is not None
        ]
    }


def find_key_in_kv_config(kv_config: KVConfig, key: str) -> Any:
    for field in kv_config["fields"]:
        if field["key"] == key:
            return field["value"]
    return None


class KVConfigLayerName(str, enum.Enum):
    # TODO docstrings
    # Config that is currently loaded by the model
    CURRENTLY_LOADED = "currentlyLoaded"

    # Override provided by the caller of the API
    API_OVERRIDE = "apiOverride"

    # Chat specific config in chats
    CONVERSATION_SPECIFIC = "conversationSpecific"

    # Cross-chat global config in chats
    CONVERSATION_GLOBAL = "conversationGlobal"

    # Override provided in the OpenAI http server
    HTTP_SERVER_REQUEST_OVERRIDE = "httpServerRequestOverride"

    # Override to allow complete mode formatting
    COMPLETE_MODE_FORMATTING = "completeModeFormatting"

    # Instance specific config (set in the server tab)
    INSTANCE = "instance"

    # User editable per model defaults
    USER_MODEL_DEFAULT = "userModelDefault"

    # Virtual model baked in configs
    VIRTUAL_MODEL = "virtualModel"

    # LM Studio provided per model defaults
    MODEL_DEFAULT = "modelDefault"


class KVConfigStackLayer(TypedDict):
    """Represents a layer in a KVConfigStack."""
    layerName: KVConfigLayerName
    config: KVConfig


class KVConfigStack(TypedDict):
    """Represents a stack of KVConfigLayers."""
    layers: List[KVConfigStackLayer]
