from typing import Optional
from ...dataclasses import KVConfig, ModelDescriptor, ModelSpecifier
from ...utils import sync_async_decorator
from ..communications import BaseClientPort


class DynamicHandle:
    """
    This represents a set of requirements for a model. It is not tied to a specific model, but rather
    to a set of requirements that a model must satisfy.

    For example, if you got the model via `client.llm.get("my-identifier")`, you will get a
    `LLMModel` for the model with the identifier `my-identifier`. If the model is unloaded, and
    another model is loaded with the same identifier, using the same `LLMModel` will use the new
    model.
    """

    _port: BaseClientPort
    _specifier: ModelSpecifier

    def __init__(self, port: BaseClientPort, specifier: ModelSpecifier):
        self._port = port
        self._specifier = specifier

    @sync_async_decorator(
        obj_method="call_rpc", process_result=lambda x: x.get("descriptor") if x is not None else None
    )
    def get_model_info(self) -> Optional[ModelDescriptor]:
        """
        Gets the information of the model that is currently associated with this `LLMModel`. If no
        model is currently associated, this will return `None`.

        Note: As models are loaded/unloaded, the model associated with this `LLMModel` may change at
        any moment.
        """
        return {"endpoint": "getModelInfo", "parameter": {"specifier": self._specifier, "throwIfNotFound": False}}

    @sync_async_decorator(obj_method="call_rpc", process_result=lambda x: x)
    def get_load_config(self) -> KVConfig:
        return {"endpoint": "getLoadConfig", "parameter": {"specifier": self._specifier}}
