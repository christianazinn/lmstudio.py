from typing import Literal, TypedDict, Union
from .ModelQuery import ModelQuery


class QueryModel(TypedDict):
    type: Literal["query"]
    query: ModelQuery


class InstanceReferenceModel(TypedDict):
    type: Literal["instanceReference"]
    instance_reference: str


ModelSpecifier = Union[QueryModel, InstanceReferenceModel]
