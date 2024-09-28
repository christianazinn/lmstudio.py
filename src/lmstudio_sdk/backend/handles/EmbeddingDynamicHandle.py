from typing import List

from ...dataclasses import find_key_in_kv_config
from ...utils import get_logger, LiteralOrCoroutine
from .DynamicHandle import DynamicHandle


logger = get_logger(__name__)


class EmbeddingDynamicHandle(DynamicHandle):
    """
    This represents a set of requirements for a model. It is not tied to a specific model, but rather
    to a set of requirements that a model must satisfy.

    For example, if you got the model via `client.embedding.get("my-identifier")`, you will get a
    `EmbeddingModel` for the model with the identifier `my-identifier`. If the model is unloaded, and
    another model is loaded with the same identifier, using the same `EmbeddingModel` will use the
    new model.

    :public:
    """

    def embed_string(self, input_string: str) -> LiteralOrCoroutine[dict[str, List[float]]]:
        """
        Embed a string into a vector representation.

        :param input_string: The string to embed.
        :return: A dictionary containing the embedding as a list of floats.
        """
        if not isinstance(input_string, str):
            logger.error(f"embed_string: input_string must be a string, got {type(input_string)}")
            raise ValueError("Input string must be a string.")
        return self._port.call_rpc(
            "embedString", {"specifier": self._specifier, "inputString": input_string}, lambda x: x
        )

    def unstable_get_context_length(self) -> LiteralOrCoroutine[int]:
        """
        Get the context length of the model.

        :return: The context length as an integer.
        """
        return self._port.call_rpc(
            "getLoadConfig",
            {"specifier": self._specifier},
            lambda x: find_key_in_kv_config(x, "embedding.load.contextLength") or -1,
        )

    def unstable_get_eval_batch_size(self) -> LiteralOrCoroutine[int]:
        """
        Get the evaluation batch size of the model.

        :return: The evaluation batch size as an integer.
        """
        return self.get_load_config(lambda x: find_key_in_kv_config(x, "embedding.load.llama.evalBatchSize") or -1)

    def unstable_tokenize(self, input_string: str) -> LiteralOrCoroutine[List[int]]:
        """
        Tokenize the input string.

        :param input_string: The string to tokenize.
        :return: A list of integers representing the tokenized string.
        """
        if not isinstance(input_string, str):
            logger.error(f"unstable_tokenize: input_string must be a string, got {type(input_string)}")
            raise ValueError("Input string must be a string.")
        return self._port.call_rpc(
            "tokenize", {"specifier": self._specifier, "inputString": input_string}, lambda x: x.get("tokens", [-1])
        )
