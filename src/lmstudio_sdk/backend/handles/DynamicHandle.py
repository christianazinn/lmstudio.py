from typing import Any, Callable, Optional

import lmstudio_sdk.dataclasses as dc
import lmstudio_sdk.utils as utils
import lmstudio_sdk.backend.communications as comms


class DynamicHandle:
    """Represents a set of requirements for a model.

    It is not tied to a specific model, but rather
    to a set of requirements that a model must satisfy.
    """

    _port: comms.BaseClientPort
    _specifier: dc.ModelSpecifier

    def __init__(
        self, port: comms.BaseClientPort, specifier: dc.ModelSpecifier
    ):
        self._port = port
        self._specifier = specifier

    def get_model_info(
        self,
    ) -> utils.LiteralOrCoroutine[Optional[dc.ModelDescriptor]]:
        """Get the information of the currently associated model.

        As models are loaded/unloaded, the model associated
        with this method may change at any moment.

        Returns:
            The model descriptor if the model is loaded, else `None`.
        """
        return self._port.call_rpc(
            "getModelInfo",
            {"specifier": self._specifier, "throwIfNotFound": False},
            lambda x: x.get("descriptor", None) if x else None,
        )

    def get_load_config(
        self, postprocess: Callable[[dict], Any] = lambda x: x
    ) -> utils.LiteralOrCoroutine[dc.KVConfig]:
        """Get the load configuration of the currently associated model.

        Most often used under the hood to get a particular load config value.

        Returns:
            The load configuration of the model.
        """
        return self._port.call_rpc(
            "getLoadConfig", {"specifier": self._specifier}, postprocess
        )
