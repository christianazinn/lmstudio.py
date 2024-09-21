from abc import ABC
from ..communications import BaseClientPort
from ...dataclasses import ModelSpecifier


class BaseDynamicHandle(ABC):
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
