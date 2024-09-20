from typing import List, Union
from abc import ABC
import asyncio

from ...lms_dataclasses import (
    ModelDescriptor,
    BaseLoadModelOpts,
    ModelQuery,
    EmbeddingLoadModelConfig,
    LLMLoadModelConfig,
    ModelSpecifier,
    KVConfigLayerName,
)
from ..handles import EmbeddingDynamicHandle, LLMDynamicHandle, EmbeddingSpecificModel, LLMSpecificModel
from ..communications import ClientPort
from ...backend_common import (
    TClientPort,
    TLoadModelConfig,
    TDynamicHandle,
    TSpecificModel,
    BaseModelNamespace,
    BaseLLMNamespace,
    BaseEmbeddingNamespace,
)


class ModelNamespace(BaseModelNamespace[TClientPort, TLoadModelConfig, TDynamicHandle, TSpecificModel], ABC):
    """
    Abstract namespace for namespaces that deal with models.

    :public:
    """

    async def connect(self) -> None:
        await self._port.connect()

    async def close(self) -> None:
        await self._port.close()

    async def load(self, path: str, opts: BaseLoadModelOpts[TLoadModelConfig] | None = None) -> TSpecificModel:
        """
        Load a model for inferencing. The first parameter is the model path. The second parameter is an
        optional object with additional options. By default, the model is loaded with the default
        preset (as selected in LM Studio) and the verbose option is set to true.

        When specifying the model path, you can use the following format:

        `<publisher>/<repo>[/model_file]`

        If `model_file` is not specified, the first (sorted alphabetically) model in the repository is
        loaded.

        To find out what models are available, you can use the `lms ls` command, or programmatically
        use the `client.system.listDownloadedModels` method.

        Here are some examples:

        Loading Llama 3:

        ```typescript
        const model = await client.llm.load("lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF");
        ```

        Loading a specific quantization (q4_k_m) of Llama 3:

        ```typescript
        const model = await client.llm.load("lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf");
        ```

        To unload the model, you can use the `client.llm.unload` method. Additionally, when the last
        client with the same `clientIdentifier` disconnects, all models loaded by that client will be
        automatically unloaded.

        Once loaded, see {@link LLMDynamicHandle} or {@link EmbeddingDynamicHandle} for how to use the
        model for inferencing or other things you can do with the model.

        :param path: The path of the model to load.
        :param opts: Options for loading the model.
        :return: A promise that resolves to the model that can be used for inferencing
        """
        # TODO logging
        promise = asyncio.Future()
        full_path: str = path

        def resolve(value):
            promise.set_result(value)

        def reject(error):
            promise.set_exception(error)

        async def handle_message(message):
            message_type = message.get("type", "")
            if message_type == "resolved":
                nonlocal full_path
                full_path = message.get("fullPath")
                if message.get("ambiguous", False):
                    # FIXME this should be a warning
                    print(f"Multiple models found for {path}. Using the first one.")
                # TODO there are a bunch of logging steps here but you don't have a logger
            elif message_type == "success":
                resolve(
                    self.create_domain_specific_model(
                        self._port,
                        message.get("instanceReference"),
                        {"identifier": message.get("identifier"), "path": path},
                    )
                )
            elif message_type == "progress":
                progress = message.get("progress")
                if opts and "on_progress" in opts:
                    on_progress = opts.get("on_progress")
                    if on_progress is not None:
                        on_progress(progress)
            elif message_type == "error":
                reject(Exception(message.get("message", "Unknown error")))

        channel_id = await self._port.create_channel(
            "loadModel",
            {
                "path": path,
                "identifier": opts["identifier"] if opts and "identifier" in opts else path,
                "loadConfigStack": {
                    "layers": [
                        {
                            "layerName": KVConfigLayerName.API_OVERRIDE,
                            "config": self.load_config_to_kv_config(
                                opts["config"] if opts and "config" in opts else self._default_load_config
                            ),
                        }
                    ]
                },
            },
            handle_message,
        )

        def on_cancel():
            # TODO async things again
            self._port.send_channel_message(channel_id, {"type": "cancel"})
            reject(Exception("Model loading was cancelled"))

        if opts and hasattr(opts, "signal"):
            signal = opts.get("signal")
            if signal is not None:
                signal.add_listener(on_cancel)

        return promise  # type: ignore

    async def unload(self, identifier: str) -> None:
        """
        Unload a model. Once a model is unloaded, it can no longer be used. If you wish to use the
        model afterwards, you will need to load it with {@link LLMNamespace#loadModel} again.

        :param identifier: The identifier of the model to unload.
        """
        assert isinstance(identifier, str)
        await self._port.call_rpc("unloadModel", {"identifier": identifier})

    async def list_loaded(self) -> List[ModelDescriptor]:
        """
        List all the currently loaded models.
        """
        return await self._port.call_rpc("listLoaded", None)  # type: ignore

    async def get(self, query: Union[ModelQuery, str]) -> TSpecificModel:
        """
        Get a specific model that satisfies the given query. The returned model is tied to the specific
        model at the time of the call.

        For more information on the query, see {@link ModelQuery}.

        :example:

        If you have loaded a model with the identifier "my-model", you can use it like this:

        ```ts
        const model = await client.llm.get({ identifier: "my-model" });
        const prediction = model.complete("...");
        ```

        Or just

        ```ts
        const model = await client.llm.get("my-model");
        const prediction = model.complete("...");
        ```

        :example:

        Use the Gemma 2B IT model (given it is already loaded elsewhere):

        ```ts
        const model = await client.llm.get({ path: "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF" });
        const prediction = model.complete("...");
        ```
        """
        # TODO figure out how to do union type checking
        if isinstance(query, str):
            query = {"identifier": query}
        query["domain"] = self._namespace
        info = await self._port.call_rpc(
            "getModelInfo", {"specifier": {"type": "query", "query": query}, "throwIfNotFound": True}
        )
        if not info or info is None:
            raise Exception("Model not found")
        return self.create_domain_specific_model(self._port, info.get("instanceReference"), info.get("descriptor"))  # type: ignore

    async def unstable_get_any(self) -> TSpecificModel:
        return await self.get({})

    async def unstable_get_or_load(
        self, identifier: str, path: str, load_opts: BaseLoadModelOpts[TLoadModelConfig] | None = None
    ) -> TSpecificModel:
        """
        Extremely early alpha. Will cause errors in console. Can potentially throw if called in
        parallel. Do not use in production yet.
        """
        try:
            model = await self.get({"identifier": identifier})
            return model
        except Exception:
            if load_opts:
                load_opts["identifier"] = identifier
            return await self.load(path, load_opts)


# TODO custom ports with type locks
class EmbeddingNamespace(
    BaseEmbeddingNamespace,
    ModelNamespace[ClientPort, EmbeddingLoadModelConfig, EmbeddingDynamicHandle, EmbeddingSpecificModel],
):
    def create_domain_specific_model(
        self, port: ClientPort, instance_reference: str, descriptor: ModelDescriptor
    ) -> EmbeddingSpecificModel:
        return EmbeddingSpecificModel(port, instance_reference, descriptor)

    def create_domain_dynamic_handle(self, port: TClientPort, specifier: ModelSpecifier) -> EmbeddingDynamicHandle:
        return EmbeddingDynamicHandle(port, specifier)


class LLMNamespace(
    BaseLLMNamespace,
    ModelNamespace[ClientPort, LLMLoadModelConfig, LLMDynamicHandle, LLMSpecificModel],
):
    def create_domain_specific_model(
        self, port: ClientPort, instance_reference: str, descriptor: ModelDescriptor
    ) -> LLMSpecificModel:
        return LLMSpecificModel(port, instance_reference, descriptor)

    def create_domain_dynamic_handle(self, port: TClientPort, specifier: ModelSpecifier) -> LLMDynamicHandle:
        return LLMDynamicHandle(port, specifier)
