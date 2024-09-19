from typing import Literal, NotRequired, TypedDict


class DownloadedModel(TypedDict):
    """
    Represents a model that exists locally and can be loaded.
    """

    type: Literal["llm", "embedding"]
    """
    The type of the model.
    """

    path: str
    """
    The path of the model. Use to load the model.
    """

    size_bytes: int
    """
    The size of the model in bytes.
    """

    architecture: NotRequired[str]
    """
    The architecture of the model.
    """
