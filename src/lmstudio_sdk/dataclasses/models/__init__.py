"""Dataclasses for models and model management.

Classes:
    DownloadedModel: Represents a model that exists locally and can be loaded.
    InstanceReferenceModel: A model instance reference.
    ModelDescriptor: Describes a specific loaded model.
    ModelDomainType: The domain of a model.
    ModelQuery: A query for a loaded model.
    ModelSpecifier: A specifier for a model.
    QueryModel: A query for a model.
"""

from .DownloadedModel import DownloadedModel
from .ModelDescriptor import ModelDescriptor
from .ModelQuery import ModelDomainType, ModelQuery
from .ModelSpecifier import ModelSpecifier, InstanceReferenceModel, QueryModel

__all__ = [
    "DownloadedModel",
    "InstanceReferenceModel",
    "ModelDescriptor",
    "ModelDomainType",
    "ModelQuery",
    "ModelSpecifier",
    "QueryModel",
]
