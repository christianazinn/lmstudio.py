from typing import List, Literal, Union
from abc import ABC, abstractmethod
from relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class PredictionStepController(ConfiguredBaseModel):
    pass


class ProcessorInputFile(ConfiguredBaseModel):
    identifier: str
    type: "ProcessorInputFileType"
    sizeBytes: int


ProcessorInputFileType = Literal["image", "text/plain", "text/other", "application/pdf", "application/word", "unknown"]


ProcessorInputMessageRole = Literal["system", "user", "assistant"]


class ProcessorInputMessage(ConfiguredBaseModel):
    role: ProcessorInputMessageRole
    text: str
    files: List[ProcessorInputFile]


class ProcessorInputContext(ConfiguredBaseModel):
    history: List[ProcessorInputMessage]


class PromptPreprocessController(ConfiguredBaseModel):
    pass


class PromptPreprocessor(ABC):
    @property
    @abstractmethod
    def identifier(self) -> str:
        pass

    @abstractmethod
    async def preprocess(self, ctl: PromptPreprocessController) -> Union[str, ProcessorInputMessage]:
        pass


class StatusStepState(ConfiguredBaseModel):
    status: "StatusStepStatus"
    text: str


StatusStepStatus = Literal["waiting", "loading", "done", "error", "canceled"]
