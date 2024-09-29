from typing import Any, Callable, Optional
from ...dataclasses import KVConfig, ModelDescriptor, ModelSpecifier
from ...utils import LiteralOrCoroutine
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

    def get_model_info(self) -> LiteralOrCoroutine[Optional[ModelDescriptor]]:
        """
        Gets the information of the model that is currently associated with this `LLMModel`. If no
        model is currently associated, this will return `None`.

        Note: As models are loaded/unloaded, the model associated with this `LLMModel` may change at
        any moment.
        """
        return self._port.call_rpc(
            "getModelInfo",
            {"specifier": self._specifier, "throwIfNotFound": False},
            lambda x: x.get("descriptor", None) if x else None,
        )

    def get_load_config(
        self, postprocess: Callable[[dict], Any] = lambda x: x
    ) -> LiteralOrCoroutine[KVConfig]:
        return self._port.call_rpc(
            "getLoadConfig", {"specifier": self._specifier}, postprocess
        )
