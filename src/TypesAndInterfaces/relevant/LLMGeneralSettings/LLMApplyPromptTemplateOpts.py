from typing import NotRequired
from typing_extensions import TypedDict


class LLMApplyPromptTemplateOpts(TypedDict):
    """
    Options for applying a prompt template.
    """

    omit_bos_token: NotRequired[bool]
    """
    Whether to omit the BOS token when formatting.
    """

    omit_eos_token: NotRequired[bool]
    """
    Whether to omit the EOS token when formatting.
    """
