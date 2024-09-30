from typing import Literal, TypedDict, Union

from .ModelQuery import ModelQuery


class QueryModel(TypedDict):
    """Represents a query for a model."""

    type: Literal["query"]
    query: ModelQuery


class InstanceReferenceModel(TypedDict):
    """Represents a model by instance reference."""

    type: Literal["instanceReference"]
    instance_reference: str


ModelSpecifier = Union[QueryModel, InstanceReferenceModel]
"""Represents a model specifier."""
