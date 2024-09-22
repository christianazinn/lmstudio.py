from typing import NotRequired, TypedDict, Literal


ModelDomainType = Literal["llm", "embedding"]


class ModelQuery(TypedDict):
    """
    Represents a query for a loaded LLM.

    @public
    """

    domain: NotRequired[ModelDomainType]
    """The domain of the model."""

    identifier: NotRequired[str]
    """
    If specified, the model must have exactly this identifier.

    Note: The identifier of a model is set when loading the model. It defaults to the filename of
    the model if not specified. However, this default behavior should not be relied upon. If you
    wish to query a model by its path, you should specify the path instead of the identifier:

    Instead of

    ```python
    model = client.llm.get(identifier="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF")
    # OR
    model = client.llm.get("lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF")
    ```

    Use

    ```python
    model = client.llm.get(path="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF")
    ```
    """

    path: NotRequired[str]
    """
    If specified, the model must have this path.

    When specifying the model path, you can use the following format:

    `<publisher>/<repo>[/model_file]`

    If `model_file` is not specified, any quantization of the model will match this query.

    Here are some examples:

    Query any loaded Llama 3 model:

    ```python
    model = client.llm.get(
        path="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"
    )
    ```

    Query any loaded model with a specific quantization of the Llama 3 model:

    ```python
    model = client.llm.get(
        path="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
    )
    ```
    """
