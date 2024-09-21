from typing import List

from ...common import BaseEmbeddingDynamicHandle, find_key_in_kv_config, sync_async_decorator
from .AsyncDynamicHandle import DynamicHandle


class EmbeddingDynamicHandle(DynamicHandle, BaseEmbeddingDynamicHandle):
    """
    This represents a set of requirements for a model. It is not tied to a specific model, but rather
    to a set of requirements that a model must satisfy.

    For example, if you got the model via `client.embedding.get("my-identifier")`, you will get a
    `EmbeddingModel` for the model with the identifier `my-identifier`. If the model is unloaded, and
    another model is loaded with the same identifier, using the same `EmbeddingModel` will use the
    new model.

    :public:
    """

    @sync_async_decorator(obj_method="call_rpc", process_result=lambda x: x)
    def embed_string(self, input_string: str) -> dict[str, List[float]]:
        """
        Embed a string into a vector representation.

        :param input_string: The string to embed.
        :return: A dictionary containing the embedding as a list of floats.
        """
        assert isinstance(input_string, str)
        return {"endpoint": "embedString", "parameter": {"specifier": self._specifier, "inputString": input_string}}

    @sync_async_decorator(
        obj_method="get_load_config", process_result=lambda x: find_key_in_kv_config(x, "embedding.load.contextLength") or -1
    )
    def unstable_get_context_length(self) -> int:
        """
        Get the context length of the model.

        :return: The context length as an integer.
        """
        return {}

    @sync_async_decorator(
        obj_method="get_load_config",
        process_result=lambda x: find_key_in_kv_config(x, "embedding.load.llama.evalBatchSize") or -1,
    )
    def unstable_get_eval_batch_size(self) -> int:
        """
        Get the evaluation batch size of the model.

        :return: The evaluation batch size as an integer.
        """
        return {}

    @sync_async_decorator(obj_method="call_rpc", process_result=lambda x: x.get("tokens", [-1]))
    def unstable_tokenize(self, input_string: str) -> List[int]:
        """
        Tokenize the input string.

        :param input_string: The string to tokenize.
        :return: A list of integers representing the tokenized string.
        """
        assert isinstance(input_string, str)
        return {"endpoint": "tokenize", "parameter": {"specifier": self._specifier, "inputString": input_string}}