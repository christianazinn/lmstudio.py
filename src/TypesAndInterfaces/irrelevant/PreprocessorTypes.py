from typing import List, Literal, Union, TypedDict
from abc import ABC, abstractmethod


class PredictionStepController(TypedDict):
    pass


class ProcessorInputFile(TypedDict):
    identifier: str
    type: "ProcessorInputFileType"
    sizeBytes: int


ProcessorInputFileType = Literal["image", "text/plain", "text/other", "application/pdf", "application/word", "unknown"]


ProcessorInputMessageRole = Literal["system", "user", "assistant"]


class ProcessorInputMessage(TypedDict):
    role: ProcessorInputMessageRole
    text: str
    files: List[ProcessorInputFile]


class ProcessorInputContext(TypedDict):
    history: List[ProcessorInputMessage]


class PromptPreprocessController(TypedDict):
    pass


class PromptPreprocessor(ABC):
    @property
    @abstractmethod
    def identifier(self) -> str:
        pass

    @abstractmethod
    async def preprocess(self, ctl: PromptPreprocessController) -> Union[str, ProcessorInputMessage]:
        pass


class StatusStepState(TypedDict):
    status: "StatusStepStatus"
    text: str


StatusStepStatus = Literal["waiting", "loading", "done", "error", "canceled"]
