from typing import List, Union, Generic, TypeVar
from abc import ABC, abstractmethod
from functools import partial

from ...dataclasses import (
    ModelDescriptor,
    BaseLoadModelOpts,
    ModelQuery,
    EmbeddingLoadModelConfig,
    LLMLoadModelConfig,
    ModelSpecifier,
    KVConfigLayerName,
    ModelDomainType,
    KVConfig,
    convert_dict_to_kv_config,
)
from ...utils import sync_async_decorator
from ..handles import EmbeddingDynamicHandle, LLMDynamicHandle, EmbeddingSpecificModel, LLMSpecificModel, DynamicHandle
from ..communications import BaseClientPort


TClientPort = TypeVar("TClientPort", bound="BaseClientPort")
TLoadModelConfig = TypeVar("TLoadModelConfig")
TDynamicHandle = TypeVar("TDynamicHandle", bound="DynamicHandle")
TSpecificModel = TypeVar("TSpecificModel")


def load_process_result(extra):
    channel_id = extra.get("channel_id")
    extra = extra.get("extra")
    if "signal" in extra:
        print("hello", channel_id)
        extra.get("signal").add_listener(partial(extra.get("cancel_send"), channel_id))
    if extra.get("is_async"):
        return extra.get("promise")
    return extra.get("promise").result()


# TODO ughhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh
class ModelNamespace(Generic[TClientPort, TLoadModelConfig, TDynamicHandle, TSpecificModel], ABC):
    """
    Abstract namespace for namespaces that deal with models.

    :public:
    """

    _namespace: ModelDomainType
    _default_load_config: TLoadModelConfig
    _port: TClientPort

    def __init__(self, port: TClientPort):
        self._port = port

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
        if "path" in query:
            path = query.get("path")
            if path is not None and "\\" in path:
                raise ValueError("Model path should not contain backslashes.")

        return self.create_domain_dynamic_handle(self._port, {"type": "query", "query": query})

    def create_dynamic_handle_from_instance_reference(self, instance_reference: str) -> TDynamicHandle:
        """
        Create a dynamic handle from the internal instance reference.

        :alpha:
        """
        return self.create_domain_dynamic_handle(
            self._port, {"type": "instanceReference", "instanceReference": instance_reference}
        )

    @sync_async_decorator(obj_method="connect", process_result=lambda x: None)
    def connect(self) -> None:
        pass

    @sync_async_decorator(obj_method="close", process_result=lambda x: None)
    def close(self) -> None:
        pass

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

    # TODO slightly more complicated reconciliation with return types
    @sync_async_decorator(obj_method="create_channel", process_result=load_process_result)
    def load(self, path: str, opts: BaseLoadModelOpts[TLoadModelConfig] | None = None) -> TSpecificModel:
        # TODO logging
        promise = self._port.promise_event()
        full_path: str = path

        def resolve(value):
            promise.set_result(value)

        def reject(error):
            promise.set_exception(error)

        def handle_message(message):
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

        # TODO this never gets called
        @sync_async_decorator(obj_method=(self._port, "send_channel_message"), process_result=lambda x: None)
        def cancel_send(channel_id):
            reject(Exception("Model loading was cancelled"))
            return {"channel_id": channel_id, "message": {"type": "cancel"}}

        extra = {"is_async": self._port.is_async(), "promise": promise}
        if opts and "signal" in opts:
            signal = opts.get("signal")
            if signal is not None:
                extra.update({"signal": signal, "cancel_send": cancel_send})

        print("about to pass to channel creation")

        return {
            "endpoint": "loadModel",
            "creation_parameter": {
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
            "handler": handle_message,
            "extra": extra,
        }

    @sync_async_decorator(obj_method="call_rpc", process_result=lambda x: x)
    def unload(self, identifier: str) -> None:
        """
        Unload a model. Once a model is unloaded, it can no longer be used. If you wish to use the
        model afterwards, you will need to load it with {@link LLMNamespace#loadModel} again.

        :param identifier: The identifier of the model to unload.
        """
        assert isinstance(identifier, str)
        return {"endpoint": "unloadModel", "parameter": {"identifier": identifier}}

    @sync_async_decorator(obj_method="call_rpc", process_result=lambda x: x)
    def list_loaded(self) -> List[ModelDescriptor]:
        """
        List all the currently loaded models.
        """
        return {"endpoint": "listLoaded", "parameter": None}

    # TODO: somehow you need to get self in there
    @sync_async_decorator(
        obj_method="call_rpc",
        process_result=lambda x: x.get("extra").get("process_result")(x),
    )
    def get(self, query: Union[ModelQuery, str]) -> TSpecificModel:
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

        def process_get_result(x):
            if not x or x is None:
                raise Exception("Model not found")
            return self.create_domain_specific_model(self._port, x.get("instanceReference"), x.get("descriptor"))

        return {
            "endpoint": "getModelInfo",
            "parameter": {"specifier": {"type": "query", "query": query}, "throwIfNotFound": True},
            "extra": {
                "process_result": lambda x: process_get_result(x),
            },
        }

    @sync_async_decorator(obj_method="get", process_result=lambda x: x)
    def unstable_get_any(self) -> TSpecificModel:
        return {"query": {}}

    # doesn't need to be decorated because if async, the return types are coroutines already!
    def unstable_get_or_load(
        self, identifier: str, path: str, load_opts: BaseLoadModelOpts[TLoadModelConfig] | None = None
    ) -> TSpecificModel:
        """
        Extremely early alpha. Will cause errors in console. Can potentially throw if called in
        parallel. Do not use in production yet.
        """
        try:
            return self.get({"identifier": identifier})
        except Exception:
            if load_opts:
                load_opts["identifier"] = identifier
            return self.load(path, load_opts)


# TODO custom ports with type locks
class EmbeddingNamespace(
    ModelNamespace[TClientPort, EmbeddingLoadModelConfig, EmbeddingDynamicHandle, EmbeddingSpecificModel],
):
    _namespace = "embedding"
    _default_load_config: EmbeddingLoadModelConfig = {}

    def load_config_to_kv_config(self, config: EmbeddingLoadModelConfig) -> KVConfig:
        return convert_dict_to_kv_config(
            {
                "llama.acceleration.offloadRatio": config.get("gpu_offload", {}).get("ratio"),
                "llama.acceleration.mainGpu": config.get("gpu_offload", {}).get("main_gpu"),
                "llama.acceleration.tensorSplit": config.get("gpu_offload", {}).get("tensor_split"),
                # TODO don't know if you need the embedding.load
                "embedding.load.contextLength": config.get("context_length"),
                "llama.ropeFrequencyBase": config.get("rope_frequency_base"),
                "llama.ropeFrequencyScale": config.get("rope_frequency_scale"),
                "llama.keepModelInMemory": config.get("keep_model_in_memory"),
                "llama.tryMmap": config.get("try_mmap"),
            }
        )

    def create_domain_specific_model(
        self, port: TClientPort, instance_reference: str, descriptor: ModelDescriptor
    ) -> EmbeddingSpecificModel:
        return EmbeddingSpecificModel(port, instance_reference, descriptor)

    def create_domain_dynamic_handle(self, port: TClientPort, specifier: ModelSpecifier) -> EmbeddingDynamicHandle:
        return EmbeddingDynamicHandle(port, specifier)


class LLMNamespace(
    ModelNamespace[TClientPort, LLMLoadModelConfig, LLMDynamicHandle, LLMSpecificModel],
):
    _namespace = "llm"
    _default_load_config: LLMLoadModelConfig = {}

    def load_config_to_kv_config(self, config: LLMLoadModelConfig) -> KVConfig:
        # why is this implemented like this???
        fields = {
            # TODO don't know if you need the llm.load
            "llm.load.contextLength": config.get("context_length"),
            "llama.evalBatchSize": config.get("eval_batch_size"),
            "llama.flashAttention": config.get("flash_attention"),
            "llama.ropeFrequencyBase": config.get("rope_frequency_base"),
            "llama.ropeFrequencyScale": config.get("rope_frequency_scale"),
            "llama.keepModelInMemory": config.get("keep_model_in_memory"),
            "seed": config.get("seed"),
            "llama.useFp16ForKVCache": config.get("use_fp16_for_kv_cache"),
            "llama.tryMmap": config.get("try_mmap"),
            "numExperts": config.get("num_experts"),
        }
        if "gpu_offload" in config:
            gpu_offload = config.get("gpu_offload")
            if isinstance(gpu_offload, float):
                fields["llama.acceleration.offloadRatio"] = gpu_offload
            else:
                assert not isinstance(gpu_offload, int) and gpu_offload is not None
                fields["llama.acceleration.offloadRatio"] = gpu_offload.get("ratio")
                fields["llama.acceleration.mainGpu"] = gpu_offload.get("main_gpu")
                fields["llama.acceleration.tensorSplit"] = gpu_offload.get("tensor_split")
        return convert_dict_to_kv_config(fields)

    def create_domain_specific_model(
        self, port: TClientPort, instance_reference: str, descriptor: ModelDescriptor
    ) -> LLMSpecificModel:
        return LLMSpecificModel(port, instance_reference, descriptor)

    def create_domain_dynamic_handle(self, port: TClientPort, specifier: ModelSpecifier) -> LLMDynamicHandle:
        return LLMDynamicHandle(port, specifier)

    # TODO registerPromptPreprocessor
