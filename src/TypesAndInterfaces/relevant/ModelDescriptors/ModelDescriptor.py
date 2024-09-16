from pydantic import Field
from Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class ModelDescriptor(ConfiguredBaseModel):
    """
    Describes a specific loaded LLM.
    """

    identifier: str = Field(
        ...,
        description="""
        The identifier of the model (Set when loading the model. Defaults to the same as the path.)

        Identifier identifies a currently loaded model.
        """,
    )

    path: str = Field(
        ...,
        description="""
        The path of the model. (i.e. which model is this)

        An path is associated with a specific model that can be loaded.
        """,
    )
