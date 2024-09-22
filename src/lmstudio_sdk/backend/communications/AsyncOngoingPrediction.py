from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Callable, Generic, List, Optional, TypeVar
from ...dataclasses import ModelDescriptor, KVConfig, LLMPredictionStats, PredictionResult


TFragment = TypeVar("TFragment")
TFinal = TypeVar("TFinal")


# TODO polish
class StreamablePromise(Generic[TFragment, TFinal], ABC):
    def __init__(self):
        self.queue: asyncio.Queue[Optional[TFragment]] = asyncio.Queue()
        self.promise_final: asyncio.Future[TFinal] = asyncio.Future()
        self.status: str = "pending"
        self.buffer: List[TFragment] = []

    @abstractmethod
    async def collect(self, fragments: List[TFragment]) -> TFinal:
        pass

    def push(self, fragment: TFragment) -> None:
        if self.status != "pending":
            return
        self.buffer.append(fragment)
        self.queue.put_nowait(fragment)

    def finished(self, error: Optional[Any] = None) -> None:
        if self.status != "pending":
            return

        if error:
            self.status = "rejected"
            self.promise_final.set_exception(error)
        else:
            self.status = "resolved"
            asyncio.create_task(self._resolve())

        self.queue.put_nowait(None)  # Signal end of stream

    async def _resolve(self):
        try:
            result = await self.collect(self.buffer)
            self.promise_final.set_result(result)
        except Exception as e:
            self.promise_final.set_exception(e)

    def __await__(self):
        return self.promise_final.__await__()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __aiter__(self) -> AsyncIterator[TFragment]:
        return self

    async def __anext__(self) -> TFragment:
        item = await self.queue.get()
        if item is None:
            if self.status == "rejected":
                raise Exception()
            raise StopAsyncIteration
        return item


class AsyncOngoingPrediction(StreamablePromise[str, PredictionResult]):
    """
    Represents an ongoing prediction.

    This class is Promise-like, meaning you can use it as a promise. It resolves to a PredictionResult,
    which contains the generated text in the `.content` property.

    Example usage:

    ```python
    result = await model.complete("When will The Winds of Winter be released?")
    print(result.content)
    ```

    You can also use instance methods like `then` and `catch` to handle the result or error of the prediction.

    Alternatively, you can stream the result (process the results as more content is being generated):

    ```python
    async for fragment in model.complete("When will The Winds of Winter be released?"):
        print(fragment, end='', flush=True)
    ```
    """

    def __init__(self, on_cancel: Callable[[], None]):
        super().__init__()
        self._on_cancel = on_cancel
        self._stats: Optional[LLMPredictionStats] = None
        self._model_info: Optional[ModelDescriptor] = None
        self._load_model_config: Optional[KVConfig] = None
        self._prediction_config: Optional[KVConfig] = None

    async def collect(self, fragments: List[str]) -> PredictionResult:
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
    ) -> tuple[AsyncOngoingPrediction, Callable[..., None], Callable[..., None], Callable[[str], None]]:
        ongoing_prediction = AsyncOngoingPrediction(on_cancel)

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

    def result(self) -> asyncio.Future[PredictionResult]:
        """
        Get the final prediction results. If you have been streaming the results, awaiting on this
        method will take no extra effort, as the results are already available in the internal buffer.

        Example:

        ```python
        prediction = model.complete("When will The Winds of Winter be released?")
        async for fragment in prediction:
            print(fragment, end='', flush=True)
        result = await prediction.result()
        print(result.stats)
        ```

        Technically, awaiting on this method is the same as awaiting on the instance itself:

        ```python
        await prediction.result()

        # Is the same as:

        await prediction
        ```
        """
        return self.promise_final

    async def cancel(self) -> None:
        """
        Cancels the prediction. This will stop the prediction with stop reason `userStopped`.
        See LLMPredictionStopReason for other reasons that a prediction might stop.
        """
        await self._on_cancel()
