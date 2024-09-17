from typing import List, Any
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class KVConfigField(ConfiguredBaseModel):
    """
    TODO: Documentation
    """

    key: str
    value: Any = None


class KVConfig(ConfiguredBaseModel):
    """
    TODO: Documentation
    """

    fields: List[KVConfigField]
