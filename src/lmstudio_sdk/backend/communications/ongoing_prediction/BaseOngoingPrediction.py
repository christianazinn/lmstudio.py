from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, List, Optional, TypeVar

import lmstudio_sdk.dataclasses as dc

TFragment = TypeVar("TFragment")
TFinal = TypeVar("TFinal")


class BaseStreamableIterator(Generic[TFragment, TFinal], ABC):
    """An abstract streamable iterator."""

    def __init__(self, on_cancel: Callable[[], None]):
        self.status: str = "pending"
        self.buffer: List[TFragment] = []

        # technically these are ongoing prediction specific,
        # but the inheritance hierarchy makes it easier to put them here
        self._on_cancel = on_cancel
        self._stats: Optional[dc.LLMPredictionStats] = None
        self._model_info: Optional[dc.ModelDescriptor] = None
        self._load_model_config: Optional[dc.KVConfig] = None
        self._prediction_config: Optional[dc.KVConfig] = None

    @abstractmethod
    def collect(self, fragments: List[str]) -> dc.PredictionResult:
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
    """An abstract ongoing prediction."""

    @classmethod
    def create(
        cls,
        on_cancel: Callable[[], None],
    ) -> tuple[
        "BaseOngoingPrediction",
        Callable[..., None],
        Callable[..., None],
        Callable[[str], None],
    ]:
        """Create a new ongoing prediction instance.

        Registers the finished, failed, and push callbacks
        with the ongoing prediction instance as well."""
        ongoing_prediction = cls(on_cancel)

        def finished(
            stats: dc.LLMPredictionStats,
            model_info: dc.ModelDescriptor,
            load_model_config: dc.KVConfig,
            prediction_config: dc.KVConfig,
        ) -> None:
            ongoing_prediction._stats = stats
            ongoing_prediction._model_info = model_info
            ongoing_prediction._load_model_config = load_model_config
            ongoing_prediction._prediction_config = prediction_config
            ongoing_prediction.finished()

        def failed(error: Any = None) -> None:
            ongoing_prediction.finished(error)

        def push(fragment: str) -> None:
            ongoing_prediction.push(fragment)

        return ongoing_prediction, finished, failed, push

    @abstractmethod
    def result(self) -> TFinal:
        pass

    @abstractmethod
    def cancel(self) -> None:
        pass
