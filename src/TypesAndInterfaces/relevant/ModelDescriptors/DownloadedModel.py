from typing import Literal, Optional
from pydantic import Field
from Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class DownloadedModel(ConfiguredBaseModel):
    """
    Represents a model that exists locally and can be loaded.
    """

    type: Literal["llm", "embedding"] = Field(..., description="The type of the model.")
    path: str = Field(..., description="The path of the model. Use to load the model.")
    sizeBytes: int = Field(..., description="The size of the model in bytes.")
    architecture: Optional[str] = Field(None, description="The architecture of the model.")
