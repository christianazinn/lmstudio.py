import time
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar, Union

import lmstudio_sdk.dataclasses as dc
import lmstudio_sdk.utils as utils
import lmstudio_sdk.backend.communications as comms
import lmstudio_sdk.backend.handles as handles

from .BaseNamespace import BaseNamespace


logger = utils.get_logger(__name__)


TLoadModelConfig = TypeVar("TLoadModelConfig")
TDynamicHandle = TypeVar("TDynamicHandle", bound=handles.DynamicHandle)
TSpecificModel = TypeVar("TSpecificModel", bound=handles.SpecificModel)


def load_process_result(extra):
    logger.debug(extra)
    channel_id = extra.get("channelId")
    extra = extra.get("extra")
    if "signal" in extra:
        extra.get("signal").add_listener(
            lambda: extra.get("cancel_send")(channel_id)
        )
        logger.debug("Added cancel listener for channel %d.", channel_id)
    if extra.get("is_async"):
        return extra.get("promise")
    # handling PseudoFuture
    return extra.get("promise").result()


class ModelNamespace(
    BaseNamespace,
    Generic[TLoadModelConfig, TDynamicHandle, TSpecificModel],
    ABC,
):
    # TODO: docstring
    """
    Abstract namespace for namespaces that deal with models.

    :public:
    """

    _namespace: dc.ModelDomainType
    _default_load_config: TLoadModelConfig

    @abstractmethod
    def _load_config_to_kv_config(
        self, config: TLoadModelConfig
    ) -> dc.KVConfig:
        """
        Method for converting the domain-specific load config to KVConfig.
        """
        pass

    @abstractmethod
    def _create_domain_specific_model(
        self,
        port: comms.BaseClientPort,
        instance_reference: str,
        descriptor: dc.ModelDescriptor,
    ) -> TSpecificModel:
        """
        Method for creating a domain-specific model.
        """
        pass

    @abstractmethod
    def _create_domain_dynamic_handle(
        self, port: comms.BaseClientPort, specifier: dc.ModelSpecifier
    ) -> TDynamicHandle:
        """
        Method for creating a domain-specific dynamic handle.
        """
        pass

    def create_dynamic_handle(
        self, query: Union[dc.ModelQuery, str]
    ) -> TDynamicHandle:
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
        if isinstance(query, str):
            query = {"identifier": query}
        else:
            utils._assert(
                isinstance(query, dict),
                "query must be str or dict, got %s",
                type(query),
                logger,
            )
        if "path" in query:
            path = query.get("path")
            if path is not None and "\\" in path:
                logger.error(
                    "Model path should not contain backslashes, received: %s",
                    path,
                )
                raise ValueError("Model path should not contain backslashes.")

        return self._create_domain_dynamic_handle(
            self._port, {"type": "query", "query": query}
        )

    def create_dynamic_handle_from_instance_reference(
        self, instance_reference: str
    ) -> TDynamicHandle:
        """
        Create a dynamic handle from the internal instance reference.

        :alpha:
        """
        return self._create_domain_dynamic_handle(
            self._port,
            {
                "type": "instanceReference",
                "instanceReference": instance_reference,
            },
        )

    def load(
        self,
        path: str,
        opts: Optional[dc.BaseLoadModelOpts[TLoadModelConfig]] = None,
    ) -> utils.LiteralOrCoroutine[TSpecificModel]:
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

        utils._assert(
            isinstance(path, str),
            "load: path must be a string, got %s",
            type(path),
            logger,
        )

        promise = self._port._promise_event()
        full_path: str = path
        start_time: float = 0

        def resolve(value):
            promise.set_result(value)

        def reject(error):
            promise.set_exception(error)

        def handle_message(message):
            nonlocal full_path
            nonlocal start_time
            message_type = message.get("type", "")
            if message_type == "resolved":
                full_path = message.get("fullPath")
                if message.get("ambiguous", False):
                    logger.warning(
                        "Multiple models found for %s. Using the first one.",
                        path,
                    )
                logger.debug("Start loading model %s...", full_path)
                start_time = time.time()
            elif message_type == "success":
                logger.debug(
                    "Model %s loaded in %.3f s.",
                    full_path,
                    time.time() - start_time,
                )
                resolve(
                    self._create_domain_specific_model(
                        self._port,
                        message.get("instanceReference"),
                        {
                            "identifier": message.get("identifier"),
                            "path": path,
                        },
                    )
                )
            elif message_type == "progress":
                progress = message.get("progress")
                logger.debug(
                    "Model %s loading progress: %.3f%.", full_path, progress
                )
                if opts and "on_progress" in opts:
                    on_progress = opts.get("on_progress")
                    if on_progress is not None:
                        on_progress(progress)
            elif message_type == "channelError":
                logger.error(
                    "Failed to load model %s: %s",
                    full_path,
                    utils.pretty_print_error(message.get("error")),
                )
                reject(utils.ChannelError(message.get("error").get("title")))

        def cancel_send(channel_id):
            logger.info(
                "Attempting to send cancel message to channel %d.", channel_id
            )
            # we choose not to reject with an Exception because the user should not have to handle it
            resolve(None)
            return self._port.send_channel_message(
                channel_id, {"type": "cancel"}
            )

        extra = {"is_async": self._port.is_async(), "promise": promise}
        if opts and "signal" in opts:
            signal = opts.get("signal")
            if signal is not None:
                extra.update({"signal": signal, "cancel_send": cancel_send})

        return self._port.create_channel(
            "loadModel",
            {
                "path": path,
                "loadConfigStack": {
                    "layers": [
                        {
                            "layerName": dc.KVConfigLayerName.API_OVERRIDE,
                            "config": self._load_config_to_kv_config(
                                opts["config"]
                                if opts and "config" in opts
                                else self._default_load_config
                            ),
                        }
                    ]
                },
            },
            handle_message,
            lambda x: load_process_result(x),
            extra=extra,
        )

    def unload(self, identifier: str) -> None:
        """
        Unload a model. Once a model is unloaded, it can no longer be used. If you wish to use the
        model afterwards, you will need to load it with {@link LLMNamespace#loadModel} again.

        :param identifier: The identifier of the model to unload.
        """
        utils._assert(
            isinstance(identifier, str),
            "unload: identifier must be a string, got %s",
            type(identifier),
            logger,
        )
        return self._port.call_rpc(
            "unloadModel", {"identifier": identifier}, lambda x: x
        )

    def list_loaded(
        self,
    ) -> utils.LiteralOrCoroutine[List[dc.ModelDescriptor]]:
        """
        List all the currently loaded models.
        """
        return self._port.call_rpc("listLoaded", None, lambda x: x)

    def get(
        self, query: Union[dc.ModelQuery, str]
    ) -> utils.LiteralOrCoroutine[TSpecificModel]:
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
        if isinstance(query, str):
            query = {"identifier": query}
        else:
            utils._assert(
                isinstance(query, dict),
                "get: query must be str or dict, got %s",
                type(query),
                logger,
            )
        query["domain"] = self._namespace

        def process_get_result(x):
            if not x or x is None:
                logger.error(
                    "Model not found for query: %s", utils.pretty_print(query)
                )
                raise Exception("Model not found")
            return self._create_domain_specific_model(
                self._port, x.get("instanceReference"), x.get("descriptor")
            )

        return self._port.call_rpc(
            "getModelInfo",
            {
                "specifier": {"type": "query", "query": query},
                "throwIfNotFound": True,
            },
            lambda x: x.get("extra").get("process_result")(x),
            extra={"process_result": process_get_result},
        )

    def unstable_get_any(self) -> utils.LiteralOrCoroutine[TSpecificModel]:
        return self.get({})

    # doesn't need to be decorated because if async, the return types are coroutines already!
    def unstable_get_or_load(
        self,
        identifier: str,
        path: str,
        load_opts: Optional[dc.BaseLoadModelOpts[TLoadModelConfig]] = None,
    ) -> utils.LiteralOrCoroutine[TSpecificModel]:
        """
        Extremely early alpha. Will cause errors in console. Can potentially throw if called in
        parallel. Do not use in production yet.
        """
        utils._assert(
            isinstance(identifier, str),
            "identifier must be a string, got %s",
            type(identifier),
            logger,
        )
        utils._assert(
            isinstance(path, str),
            "path must be a string, got ",
            type(path),
            logger,
        )
        try:
            logger.debug(
                "Attempting to get model with identifier %s.", identifier
            )
            return self.get({"identifier": identifier})
        except Exception:
            logger.debug(
                "Model not found with identifier: %s. Attempting to load model from path: %s.",
                identifier,
                path,
            )
            if load_opts:
                load_opts["identifier"] = identifier
            return self.load(path, load_opts)


class EmbeddingNamespace(
    ModelNamespace[
        dc.EmbeddingLoadModelConfig,
        handles.EmbeddingDynamicHandle,
        handles.EmbeddingSpecificModel,
    ],
):
    # TODO: docstring
    _namespace = "embedding"
    _default_load_config: dc.EmbeddingLoadModelConfig = {}

    def _load_config_to_kv_config(
        self, config: dc.EmbeddingLoadModelConfig
    ) -> dc.KVConfig:
        fields = {
            "llama.acceleration.offloadRatio": config.get(
                "gpu_offload", {}
            ).get("ratio"),
            "llama.acceleration.mainGpu": config.get("gpu_offload", {}).get(
                "main_gpu"
            ),
            "llama.acceleration.tensorSplit": config.get(
                "gpu_offload", {}
            ).get("tensor_split"),
            "embedding.load.contextLength": config.get("context_length"),
            "llama.keepModelInMemory": config.get("keep_model_in_memory"),
            "llama.tryMmap": config.get("try_mmap"),
        }
        if "rope_frequency_base" in config:
            fields["llama.ropeFrequencyBase"] = (
                utils.number_to_checkbox_numeric(
                    config.get("rope_frequency_base"), 0, 0
                )
            )
        if "rope_frequency_scale" in config:
            fields["llama.ropeFrequencyScale"] = (
                utils.number_to_checkbox_numeric(
                    config.get("rope_frequency_scale"), 0, 0
                )
            )
        return dc.convert_dict_to_kv_config(fields)

    def _create_domain_specific_model(
        self,
        port: comms.BaseClientPort,
        instance_reference: str,
        descriptor: dc.ModelDescriptor,
    ) -> handles.EmbeddingSpecificModel:
        return handles.EmbeddingSpecificModel(
            port, instance_reference, descriptor
        )

    def _create_domain_dynamic_handle(
        self, port: comms.BaseClientPort, specifier: dc.ModelSpecifier
    ) -> handles.EmbeddingDynamicHandle:
        return handles.EmbeddingDynamicHandle(port, specifier)


class LLMNamespace(
    ModelNamespace[
        dc.LLMLoadModelConfig,
        handles.LLMDynamicHandle,
        handles.LLMSpecificModel,
    ],
):
    # TODO: docstring
    _namespace = "llm"
    _default_load_config: dc.LLMLoadModelConfig = {}

    def _load_config_to_kv_config(
        self, config: dc.LLMLoadModelConfig
    ) -> dc.KVConfig:
        fields = {
            "llm.load.contextLength": config.get("context_length"),
            "llama.evalBatchSize": config.get("eval_batch_size"),
            "llama.flashAttention": config.get("flash_attention"),
            "llama.keepModelInMemory": config.get("keep_model_in_memory"),
            "llama.useFp16ForKVCache": config.get("use_fp16_for_kv_cache"),
            "llama.tryMmap": config.get("try_mmap"),
            "numExperts": config.get("num_experts"),
        }
        if "gpu_offload" in config:
            gpu_offload = config.get("gpu_offload")
            if isinstance(gpu_offload, float):
                fields["llama.acceleration.offloadRatio"] = gpu_offload
            else:
                assert (
                    not isinstance(gpu_offload, int)
                    and gpu_offload is not None
                )
                fields["llama.acceleration.offloadRatio"] = gpu_offload.get(
                    "ratio"
                )
                fields["llama.acceleration.mainGpu"] = gpu_offload.get(
                    "main_gpu"
                )
                fields["llama.acceleration.tensorSplit"] = gpu_offload.get(
                    "tensor_split"
                )

        if "rope_frequency_base" in config:
            fields["llama.ropeFrequencyBase"] = (
                utils.number_to_checkbox_numeric(
                    config.get("rope_frequency_base"), 0, 0
                )
            )
        if "rope_frequency_scale" in config:
            fields["llama.ropeFrequencyScale"] = (
                utils.number_to_checkbox_numeric(
                    config.get("rope_frequency_scale"), 0, 0
                )
            )
        if "seed" in config:
            fields["llama.seed"] = utils.number_to_checkbox_numeric(
                config.get("seed"), -1, 0
            )
        return dc.convert_dict_to_kv_config(fields)

    def _create_domain_specific_model(
        self,
        port: comms.BaseClientPort,
        instance_reference: str,
        descriptor: dc.ModelDescriptor,
    ) -> handles.LLMSpecificModel:
        return handles.LLMSpecificModel(port, instance_reference, descriptor)

    def _create_domain_dynamic_handle(
        self, port: comms.BaseClientPort, specifier: dc.ModelSpecifier
    ) -> handles.LLMDynamicHandle:
        return handles.LLMDynamicHandle(port, specifier)

    # TODO preprocessors
