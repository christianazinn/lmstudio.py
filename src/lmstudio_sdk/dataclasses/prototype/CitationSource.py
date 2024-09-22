from typing import NotRequired, TypedDict, Union


class CitationSource(TypedDict):
    """
    Represents a source of a citation.

    This class uses the dataclass decorator to automatically generate
    __init__, __repr__, and other special methods.

    :public:
    """

    fileName: str
    absoluteFilePath: str
    pageNumber: NotRequired[Union[int, tuple[int, int]]]
    lineNumber: NotRequired[Union[int, tuple[int, int]]]
