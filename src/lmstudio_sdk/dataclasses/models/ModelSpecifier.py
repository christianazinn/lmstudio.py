from typing import Literal, TypedDict, Union

from .ModelQuery import ModelQuery


# isn't this terribly named?
class QueryModel(TypedDict):
    """A query for a model."""

    type: Literal["query"]
    query: ModelQuery


class InstanceReferenceModel(TypedDict):
    """A model instance reference."""

    type: Literal["instanceReference"]
    instance_reference: str


ModelSpecifier = Union[QueryModel, InstanceReferenceModel]
"""A model specifier."""
