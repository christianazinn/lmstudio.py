from typing import Union, Optional
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class CitationSource(ConfiguredBaseModel):
    """
    Represents a source of a citation.

    This class uses the dataclass decorator to automatically generate
    __init__, __repr__, and other special methods.

    :public:
    """

    fileName: str
    absoluteFilePath: str
    pageNumber: Optional[Union[int, tuple[int, int]]] = None
    lineNumber: Optional[Union[int, tuple[int, int]]] = None
