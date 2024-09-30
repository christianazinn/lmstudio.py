from typing import TypedDict


class ModelDescriptor(TypedDict):
    """Describes a specific loaded LLM."""

    identifier: str
    """
    The identifier of the model.

    Set when loading the model. Defaults to the same as the path.
    Identifier identifies a currently loaded model.
    """

    path: str
    """The path of the model.

    A path is associated with a specific model that can be loaded.
    """
