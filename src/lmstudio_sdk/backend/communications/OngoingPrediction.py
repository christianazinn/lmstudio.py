from __future__ import annotations
from typing import Any, Callable, Generic, Iterator, List, Optional, TypeVar
from queue import Queue
from threading import Event
from abc import ABC, abstractmethod
from ...dataclasses import KVConfig, LLMPredictionStats, ModelDescriptor, PredictionResult

TFragment = TypeVar("TFragment")
TFinal = TypeVar("TFinal")


# TODO polish
class StreamableIterator(Generic[TFragment, TFinal], ABC):
    def __init__(self):
        self.queue: Queue[Optional[TFragment]] = Queue()
        self.final_result: Optional[TFinal] = None
        self.error: Optional[Any] = None
        self.status: str = "pending"
        self.buffer: List[TFragment] = []
        self.finished_event = Event()

    @abstractmethod
    def collect(self, fragments: List[TFragment]) -> TFinal:
        pass

    def push(self, fragment: TFragment) -> None:
        if self.status != "pending":
            return
        self.buffer.append(fragment)
        self.queue.put(fragment)

    def finished(self, error: Optional[Any] = None) -> None:
        if self.status != "pending":
            return

        if error:
            self.status = "rejected"
            self.error = error
        else:
            self.status = "resolved"
            self._resolve()

        self.queue.put(None)  # Signal end of stream
        self.finished_event.set()

    def _resolve(self):
        try:
            self.final_result = self.collect(self.buffer)
        except Exception as e:
            self.status = "rejected"
            self.error = e

    def __iter__(self) -> Iterator[TFragment]:
        while True:
            item = self.queue.get()
            if item is None:
                if self.status == "rejected":
                    raise self.error
                break
            yield item

    def result(self) -> TFinal:
        self.finished_event.wait()
        if self.status == "rejected":
            raise self.error
        if self.final_result is None:
            raise ValueError("Result is not available")
        return self.final_result


class OngoingPrediction(StreamableIterator[str, PredictionResult]):
    def __init__(self, on_cancel: Callable[[], None]):
        super().__init__()
        self._on_cancel = on_cancel
        self._stats: Optional[LLMPredictionStats] = None
        self._model_info: Optional[ModelDescriptor] = None
        self._load_model_config: Optional[KVConfig] = None
        self._prediction_config: Optional[KVConfig] = None

    def collect(self, fragments: List[str]) -> PredictionResult:
        if self._stats is None:
            raise ValueError("Stats should not be None")
        if self._model_info is None:
            raise ValueError("Model info should not be None")
        if self._load_model_config is None:
            raise ValueError("Load model config should not be None")
        if self._prediction_config is None:
            raise ValueError("Prediction config should not be None")
        return PredictionResult(
            content="".join(fragments),
            stats=self._stats,
            model_info=self._model_info,
            load_config=self._load_model_config,
            prediction_config=self._prediction_config,
        )

    @staticmethod
    def create(
        on_cancel: Callable[[], None],
    ) -> tuple[OngoingPrediction, Callable[..., None], Callable[..., None], Callable[[str], None]]:
        ongoing_prediction = OngoingPrediction(on_cancel)

        def finished(
            stats: LLMPredictionStats,
            model_info: ModelDescriptor,
            load_model_config: KVConfig,
            prediction_config: KVConfig,
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

    def cancel(self) -> None:
        """
        Cancels the prediction. This will stop the prediction with stop reason `userStopped`.
        See LLMPredictionStopReason for other reasons that a prediction might stop.
        """
        self._on_cancel()
