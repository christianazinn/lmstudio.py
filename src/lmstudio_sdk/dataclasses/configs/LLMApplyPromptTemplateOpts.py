from typing import NotRequired, TypedDict


class LLMApplyPromptTemplateOpts(TypedDict):
    """Options for applying a prompt template."""

    omit_bos_token: NotRequired[bool]
    """Whether to omit the BOS token when formatting."""

    omit_eos_token: NotRequired[bool]
    """Whether to omit the EOS token when formatting."""
