from typing import List

from DynamicHandles.DynamicHandle import DynamicHandle


# TODO implement
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

    async def embed_string(self, input_string: str) -> dict[str, List[float]]:
        """
        Embed a string into a vector representation.

        :param input_string: The string to embed.
        :return: A dictionary containing the embedding as a list of floats.
        """
        pass

    async def unstable_get_context_length(self) -> int:
        """
        Get the context length of the model.

        :return: The context length as an integer.
        """
        pass

    async def unstable_get_eval_batch_size(self) -> int:
        """
        Get the evaluation batch size of the model.

        :return: The evaluation batch size as an integer.
        """
        pass

    async def unstable_tokenize(self, input_string: str) -> List[int]:
        """
        Tokenize the input string.

        :param input_string: The string to tokenize.
        :return: A list of integers representing the tokenized string.
        """
        pass