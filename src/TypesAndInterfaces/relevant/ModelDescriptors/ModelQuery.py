from typing import Optional
from pydantic import Field
from ModelDescriptors.ModelDomainType import ModelDomainType
from Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class ModelQuery(ConfiguredBaseModel):
    """
    Represents a query for a loaded LLM.

    @public
    """

    domain: Optional[ModelDomainType] = Field(default=None, description="The domain of the model.")
    identifier: Optional[str] = Field(
        default=None,
        description="""
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
    """,
    )
    path: Optional[str] = Field(
        default=None,
        description="""
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
    """,
    )
