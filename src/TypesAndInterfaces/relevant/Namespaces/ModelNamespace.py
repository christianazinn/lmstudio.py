from typing import Generic, TypeVar, List, Union, Coroutine
from abc import ABC, abstractmethod
import asyncio

from TypesAndInterfaces.relevant.CallOptions.BaseLoadModelOpts import BaseLoadModelOpts
from TypesAndInterfaces.relevant.ModelDescriptors.ModelDescriptor import ModelDescriptor
from TypesAndInterfaces.relevant.ModelDescriptors.ModelQuery import ModelQuery
from TypesAndInterfaces.relevant.DynamicHandles.DynamicHandle import DynamicHandle

from TypesAndInterfaces.relevant.DynamicHandles.SpecificModel import EmbeddingSpecificModel, LLMSpecificModel
from TypesAndInterfaces.relevant.DynamicHandles.EmbeddingDynamicHandle import EmbeddingDynamicHandle
from TypesAndInterfaces.relevant.DynamicHandles.LLMDynamicHandle import LLMDynamicHandle
from TypesAndInterfaces.relevant.CallOptions.EmbeddingLoadModelConfig import EmbeddingLoadModelConfig
from TypesAndInterfaces.relevant.CallOptions.LLMLoadModelConfig import LLMLoadModelConfig
from TypesAndInterfaces.relevant.ModelDescriptors.ModelDomainType import ModelDomainType
from TypesAndInterfaces.relevant.Defaults.ClientPort import ClientPort
from TypesAndInterfaces.relevant.ModelDescriptors.ModelSpecifier import ModelSpecifier
from TypesAndInterfaces.relevant.LLMGeneralSettings.KVConfig import KVConfig

# Type variables for generic types
TClientPort = TypeVar("TClientPort", bound="ClientPort")
TLoadModelConfig = TypeVar("TLoadModelConfig")
TDynamicHandle = TypeVar("TDynamicHandle", bound="DynamicHandle")
TSpecificModel = TypeVar("TSpecificModel")


class ModelNamespace(ABC, Generic[TClientPort, TLoadModelConfig, TDynamicHandle, TSpecificModel]):
    """
    Abstract namespace for namespaces that deal with models.

    :public:
    """

    _namespace: ModelDomainType
    _default_load_config: TLoadModelConfig
    __port: TClientPort

    def __init__(self, port: TClientPort):
        self.__port = port

    @abstractmethod
    def load_config_to_kv_config(self, config: TLoadModelConfig) -> KVConfig:
        """
        Method for converting the domain-specific load config to KVConfig.
        """
        pass

    @abstractmethod
    def create_domain_specific_model(
        self, port: TClientPort, instance_reference: str, descriptor: ModelDescriptor
    ) -> TSpecificModel:
        """
        Method for creating a domain-specific model.
        """
        pass

    @abstractmethod
    def create_domain_dynamic_handle(self, port: TClientPort, specifier: ModelSpecifier) -> TDynamicHandle:
        """
        Method for creating a domain-specific dynamic handle.
        """
        pass

    async def connect(self) -> None:
        await self.__port.connect()

    async def close(self) -> None:
        await self.__port.close()

    def load(
        self, path: str, opts: BaseLoadModelOpts[TLoadModelConfig] | None = None
    ) -> Coroutine[None, None, TSpecificModel]:
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
        assert isinstance(path, str)
        # FIXME does this even work with Python generics?
        BaseLoadModelOpts[TLoadModelConfig].model_validate(opts)

        # TODO logging
        promise = asyncio.Future()
        full_path: str = path

        def resolve(value):
            promise.set_result(value)

        def reject(error):
            promise.set_exception(error)

        async def handle_message(message):
            message_type = message.get("type")
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
                        self.__port,
                        message.get("instanceReference"),
                        {"identifier": message.get("identifier"), "path": path},
                    )
                )
            elif message_type == "progress":
                progress = message.get("progress")
                if opts.on_progress:
                    opts.on_progress(progress)
            elif message_type == "error":
                reject(Exception(message.get("message", "Unknown error")))

        channel_id = self.__port.create_channel(
            "loadModel",
            {
                "path": path,
                "identifier": opts.identifier,
                "loadConfigStack": {
                    "layers": [
                        {
                            "layerName": "apiOverride",
                            "config": self.load_config_to_kv_config(
                                opts.config if opts.config else self._default_load_config
                            ),
                        }
                    ]
                },
            },
            handle_message,
        )

        def on_cancel():
            self.__port.send_channel_message(channel_id, {"type": "cancel"})
            reject(Exception("Model loading was cancelled"))

        if opts.signal:
            opts.signal.register(on_cancel)

        return promise

    def unload(self, identifier: str) -> None:
        """
        Unload a model. Once a model is unloaded, it can no longer be used. If you wish to use the
        model afterwards, you will need to load it with {@link LLMNamespace#loadModel} again.

        :param identifier: The identifier of the model to unload.
        """
        assert isinstance(identifier, str)
        return self.__port.call_rpc("unloadModel", {"identifier": identifier})

    def list_loaded(self) -> Coroutine[None, None, List[ModelDescriptor]]:
        """
        List all the currently loaded models.
        """
        return self.__port.call_rpc("listLoaded", None)

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
        info = await self.__port.call_rpc(
            "getModelInfo", {"specifier": {"type": "query", "query": query}, "throwIfNotFound": True}
        )
        if not info or info is None:
            raise Exception("Model not found")
        return self.create_domain_specific_model(self.__port, info.get("instanceReference"), info.get("descriptor"))

    async def unstable_get_any(self) -> TSpecificModel:
        return await self.get({})

    def create_dynamic_handle(self, query: Union[ModelQuery, str]) -> TDynamicHandle:
        """
        Get a dynamic model handle for any loaded model that satisfies the given query.

        For more information on the query, see {@link ModelQuery}.

        Note: The returned `LLMModel` is not tied to any specific loaded model. Instead, it represents
        a "handle for a model that satisfies the given query". If the model that satisfies the query is
        unloaded, the `LLMModel` will still be valid, but any method calls on it will fail. And later,
        if a new model is loaded that satisfies the query, the `LLMModel` will be usable again.

        You can use {@link LLMDynamicHandle#getModelInfo} to get information about the model that is
        currently associated with this handle.

        :example:

        If you have loaded a model with the identifier "my-model", you can use it like this:

        ```ts
        const dh = client.llm.createDynamicHandle({ identifier: "my-model" });
        const prediction = dh.complete("...");
        ```

        :example:

        Use the Gemma 2B IT model (given it is already loaded elsewhere):

        ```ts
        const dh = client.llm.createDynamicHandle({ path: "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF" });
        const prediction = dh.complete("...");
        ```

        :param query: The query to use to get the model.
        """
        # TODO figure out how to do union type checking
        if isinstance(query, str):
            query = {"identifier": query}
        if "path" in query and query.get("path").includes("\\"):
            raise ValueError("Model path should not contain backslashes.")

        return self.create_domain_dynamic_handle(self.__port, {"type": "query", "query": query})

    def create_dynamic_handle_from_instance_reference(self, instance_reference: str) -> TDynamicHandle:
        """
        Create a dynamic handle from the internal instance reference.

        :alpha:
        """
        assert isinstance(instance_reference, str)
        return self.create_domain_dynamic_handle(
            self.__port, {"type": "instanceReference", "instanceReference": instance_reference}
        )

    async def unstable_get_or_load(
        self, identifier: str, path: str, load_opts: BaseLoadModelOpts[TLoadModelConfig] | None = None
    ) -> TSpecificModel:
        """
        Extremely early alpha. Will cause errors in console. Can potentially throw if called in
        parallel. Do not use in production yet.
        """
        assert isinstance(identifier, str)
        assert isinstance(path, str)
        if load_opts is not None:
            BaseLoadModelOpts[TLoadModelConfig].model_validate(load_opts)
        try:
            model = await self.get({"identifier": identifier})
            return model
        except Exception:
            load_opts.set("identifier", identifier)
            return await self.load(path, load_opts)


# TODO use special EmbeddingClientPort
class EmbeddingNamespace(
    ModelNamespace[ClientPort, EmbeddingLoadModelConfig, EmbeddingDynamicHandle, EmbeddingSpecificModel]
):
    _namespace = "embedding"
    _default_load_config = {}

    def load_config_to_kv_config(self, config: EmbeddingLoadModelConfig) -> KVConfig:
        return KVConfig.convert_dict_to_kv_config(
            {
                "llama.acceleration.offloadRatio": config.gpuOffload.ratio if config.gpuOffload else None,
                "llama.acceleration.mainGpu": config.gpuOffload.mainGpu if config.gpuOffload else None,
                "llama.acceleration.tensorSplit": config.gpuOffload.tensorSplit if config.gpuOffload else None,
                "contextLength": config.contextLength,
                "llama.ropeFrequencyBase": config.ropeFrequencyBase,
                "llama.ropeFrequencyScale": config.ropeFrequencyScale,
                "llama.keepModelInMemory": config.keepModelInMemory,
                "llama.tryMmap": config.tryMmap,
            }
        )

    def create_domain_specific_model(
        self, port: EmbeddingLoadModelConfig, instance_reference: str, descriptor: ModelDescriptor
    ) -> EmbeddingSpecificModel:
        return EmbeddingSpecificModel(port, instance_reference, descriptor)

    def create_domain_dynamic_handle(
        self, port: EmbeddingLoadModelConfig, specifier: ModelSpecifier
    ) -> EmbeddingDynamicHandle:
        return EmbeddingDynamicHandle(port, specifier)


class LLMNamespace(ModelNamespace[ClientPort, LLMLoadModelConfig, LLMDynamicHandle, LLMSpecificModel]):
    _namespace = "llm"
    _default_load_config = {}

    def load_config_to_kv_config(self, config: LLMLoadModelConfig) -> KVConfig:
        return KVConfig.convert_dict_to_kv_config(
            {
                "contextLength": config.contextLength,
                "llama.evalBatchSize": config.evalBatchSize,
                "llama.acceleration.offloadRatio": config.gpuOffload.ratio if config.gpuOffload else None,
                "llama.acceleration.mainGpu": config.gpuOffload.mainGpu if config.gpuOffload else None,
                "llama.acceleration.tensorSplit": config.gpuOffload.tensorSplit if config.gpuOffload else None,
                "llama.flashAttention": config.flashAttention,
                "llama.ropeFrequencyBase": config.ropeFrequencyBase,
                "llama.ropeFrequencyScale": config.ropeFrequencyScale,
                "llama.keepModelInMemory": config.keepModelInMemory,
                "seed": config.seed,
                "llama.useFp16ForKVCache": config.useFp16ForKVCache,
                "llama.tryMmap": config.tryMmap,
                "numExperts": config.numExperts,
            }
        )

    def create_domain_specific_model(
        self, port: LLMLoadModelConfig, instance_reference: str, descriptor: ModelDescriptor
    ) -> LLMSpecificModel:
        return LLMSpecificModel(port, instance_reference, descriptor)

    def create_domain_dynamic_handle(self, port: LLMLoadModelConfig, specifier: ModelSpecifier) -> LLMDynamicHandle:
        return LLMDynamicHandle(port, specifier)

    # TODO registerPromptPreprocessor
