from typing import Optional
from pydantic import Field
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class LLMApplyPromptTemplateOpts(ConfiguredBaseModel):
    """
    Options for applying a prompt template.
    """

    omit_bos_token: Optional[bool] = Field(
        default=None,
        description="""
    Whether to omit the BOS token when formatting.

    Default: False
    """,
    )

    omit_eos_token: Optional[bool] = Field(
        default=None,
        description="""
    Whether to omit the EOS token when formatting.

    Default: False
    """,
    )
