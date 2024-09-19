from typing import Literal, Union, TypedDict
from .ModelQuery import ModelQuery


class QueryModel(TypedDict):
    type: Literal["query"]
    query: ModelQuery


class InstanceReferenceModel(TypedDict):
    type: Literal["instanceReference"]
    instanceReference: str


ModelSpecifier = Union[QueryModel, InstanceReferenceModel]
