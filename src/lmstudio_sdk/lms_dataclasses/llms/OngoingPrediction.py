from __future__ import annotations
from asyncio import Future
from typing import Optional, Callable, List, Any
from ...typescript_ported import StreamablePromise
from ..models import ModelDescriptor
from .KVConfig import KVConfig
from .LLMPredictionStats import LLMPredictionStats
from .PredictionResult import PredictionResult


class OngoingPrediction(StreamablePromise[str, PredictionResult]):
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

    def result(self) -> Future[PredictionResult]:
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
        self._on_cancel()
