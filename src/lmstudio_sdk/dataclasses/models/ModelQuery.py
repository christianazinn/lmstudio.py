from typing import Literal, NotRequired, TypedDict


ModelDomainType = Literal["llm", "embedding"]
"""The domain of the model."""


class ModelQuery(TypedDict):
    """A query for a loaded model."""

    domain: NotRequired[ModelDomainType]
    """The domain of the model."""

    identifier: NotRequired[str]
    """The identifier of the model to query, if specified.

    The identifier of a model is set when loading the model.
    It defaults to the filename of the model if not specified.
    However, this default behavior should not be relied upon.
    If you wish to query a model by its path,
    you should specify the path instead of the identifier:

    Instead of

    ```python
    model = client.llm.get(
        {"identifier": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"}
    )
    ```

    Use

    ```python
    model = client.llm.get(
        {"path": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"}
    )
    ```
    """

    path: NotRequired[str]
    """The path of the model to query, if specified.

    When specifying the model path, you can use the format
    `<publisher>/<repo>[/model_file]`.
    If `model_file` is not specified,
    any quantization of the model will match this query.

    For instance, to query any loaded Llama 3 model:

    ```python
    model = client.llm.get(
        {"path": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"}
    )
    ```
    """
