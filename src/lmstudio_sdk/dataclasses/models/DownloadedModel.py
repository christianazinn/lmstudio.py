from typing import Literal, Optional


class DownloadedModel:
    """Represents a model that exists locally and can be loaded."""

    type: Literal["llm", "embedding"]
    """The type of the model."""

    path: str
    """The path of the model. Use to load the model."""

    size_bytes: int
    """The size of the model in bytes."""

    architecture: Optional[str]
    """The architecture of the model."""

    def __init__(
        self,
        type: Literal["llm", "embedding"],
        path: str,
        sizeBytes: int,
        architecture: Optional[str] = None,
    ):
        self.type = type
        self.path = path
        self.size_bytes = sizeBytes
        self.architecture = architecture
