from typing import Generic, TypeVar, Union
from abc import ABC, abstractmethod

from ...dataclasses import (
    ModelDescriptor,
    ModelQuery,
    EmbeddingLoadModelConfig,
    LLMLoadModelConfig,
    ModelDomainType,
    ModelSpecifier,
    KVConfig,
    convert_dict_to_kv_config,
)
from ..handles import BaseDynamicHandle
from ..communications import BaseClientPort

# Type variables for generic types
TClientPort = TypeVar("TClientPort", bound="BaseClientPort")
TLoadModelConfig = TypeVar("TLoadModelConfig")
TDynamicHandle = TypeVar("TDynamicHandle", bound="BaseDynamicHandle")
TSpecificModel = TypeVar("TSpecificModel")


class BaseModelNamespace(ABC, Generic[TClientPort, TLoadModelConfig, TDynamicHandle, TSpecificModel]):
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


class BaseEmbeddingNamespace(ABC):
    _namespace = "embedding"
    _default_load_config: EmbeddingLoadModelConfig = {}

    def load_config_to_kv_config(self, config: EmbeddingLoadModelConfig) -> KVConfig:
        return convert_dict_to_kv_config(
            {
                "llama.acceleration.offloadRatio": config.get("gpu_offload", {}).get("ratio"),
                "llama.acceleration.mainGpu": config.get("gpu_offload", {}).get("main_gpu"),
                "llama.acceleration.tensorSplit": config.get("gpu_offload", {}).get("tensor_split"),
                "contextLength": config.get("context_length"),
                "llama.ropeFrequencyBase": config.get("rope_frequency_base"),
                "llama.ropeFrequencyScale": config.get("rope_frequency_scale"),
                "llama.keepModelInMemory": config.get("keep_model_in_memory"),
                "llama.tryMmap": config.get("try_mmap"),
            }
        )


class BaseLLMNamespace(ABC):
    _namespace = "llm"
    _default_load_config: LLMLoadModelConfig = {}

    def load_config_to_kv_config(self, config: LLMLoadModelConfig) -> KVConfig:
        # why is this implemented like this???
        fields = {
            "contextLength": config.get("context_length"),
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

    # TODO registerPromptPreprocessor
