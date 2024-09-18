from typing import Literal, Union
from pydantic import Field
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel
from TypesAndInterfaces.relevant.ModelDescriptors.ModelQuery import ModelQuery


class QueryModel(ConfiguredBaseModel):
    type: Literal["query"] = Field(..., description="Discriminator for query type")
    query: ModelQuery


class InstanceReferenceModel(ConfiguredBaseModel):
    type: Literal["instanceReference"] = Field(..., description="Discriminator for instance reference type")
    instanceReference: str


ModelSpecifier = Union[QueryModel, InstanceReferenceModel]
