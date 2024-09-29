from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, List, Optional, TypeVar

from ....dataclasses import PredictionResult

TFragment = TypeVar("TFragment")
TFinal = TypeVar("TFinal")


class BaseStreamableIterator(Generic[TFragment, TFinal], ABC):
    def __init__(self):
        self.status: str = "pending"
        self.buffer: List[TFragment] = []

    @abstractmethod
    def collect(self, fragments: List[str]) -> PredictionResult:
        pass

    @abstractmethod
    def push(self, fragment: TFragment) -> None:
        pass

    @abstractmethod
    def finished(self, error: Optional[Any] = None) -> None:
        pass

    @abstractmethod
    def _resolve(self) -> None:
        pass


class BaseOngoingPrediction(BaseStreamableIterator[TFragment, TFinal], ABC):
    @abstractmethod
    def create(on_cancel: Callable[[], None]) -> TFinal:
        pass

    @abstractmethod
    def result(self) -> TFinal:
        pass

    @abstractmethod
    def cancel(self) -> None:
        pass
