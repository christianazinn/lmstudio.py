from typing import List

from ...lms_dataclasses import find_key_in_kv_config
from ...backend_common import BaseEmbeddingDynamicHandle
from .DynamicHandle import DynamicHandle


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

    def embed_string(self, input_string: str) -> dict[str, List[float]]:
        """
        Embed a string into a vector representation.

        :param input_string: The string to embed.
        :return: A dictionary containing the embedding as a list of floats.
        """
        return self._port.call_rpc("embedString", {"specifier": self._specifier, "inputString": input_string})

    def unstable_get_context_length(self) -> int:
        """
        Get the context length of the model.

        :return: The context length as an integer.
        """
        context_length = find_key_in_kv_config(self.get_load_config(), "contextLength")
        return context_length if context_length is not None else -1

    def unstable_get_eval_batch_size(self) -> int:
        """
        Get the evaluation batch size of the model.

        :return: The evaluation batch size as an integer.
        """
        batch_size = find_key_in_kv_config(self.get_load_config(), "embedding.load.llama.evalBatchSize")
        return batch_size if batch_size is not None else -1

    def unstable_tokenize(self, input_string: str) -> List[int]:
        """
        Tokenize the input string.

        :param input_string: The string to tokenize.
        :return: A list of integers representing the tokenized string.
        """
        assert isinstance(input_string, str)
        return (self._port.call_rpc("tokenize", {"specifier": self._specifier, "inputString": input_string})).get(
            "tokens", [-1]
        )
