from __future__ import annotations
from abc import ABC
from threading import Event
from typing import Any, Callable, Iterator, List, Optional
from typing_extensions import override
from queue import Queue

import lmstudio_sdk.dataclasses as dc

from .BaseOngoingPrediction import (
    BaseOngoingPrediction,
    BaseStreamableIterator,
    TFinal,
    TFragment,
)


class StreamableIterator(BaseStreamableIterator[TFragment, TFinal], ABC):
    """An abstract synchronous streamable iterator."""

    def __init__(self, on_cancel: Callable[[], None]):
        super().__init__(on_cancel)
        self.queue: Queue[Optional[TFragment]] = Queue()
        self.final_result: Optional[TFinal] = None
        self.error: Optional[Any] = None
        self.finished_event = Event()

    @override
    def push(self, fragment: TFragment) -> None:
        if self.status != "pending":
            return
        self.buffer.append(fragment)
        self.queue.put(fragment)

    @override
    def finished(self, error: Optional[Any] = None) -> None:
        if self.status != "pending":
            return

        if error:
            self.status = "rejected"
            self.error = error
        else:
            self.status = "resolved"
            self._resolve()

        self.queue.put(None)
        self.finished_event.set()

    @override
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


class SyncOngoingPrediction(
    StreamableIterator[str, dc.PredictionResult],
    BaseOngoingPrediction[str, dc.PredictionResult],
):
    """
    Represents an ongoing prediction.

    This resolves to a PredictionResult, which contains the generated text
    in the `.content` property.

    Example usage:

    ```python
    completion = model.complete(
        "When will The Winds of Winter be released?"
    )
    result = completion.result()
    print(result.content)
    ```

    Alternatively, you can stream the result
    (process the results as more content is being generated):

    ```python
    for fragment in model.complete(
        "When will The Winds of Winter be released?"
    ):
        print(fragment, end='', flush=True)
    ```
    """

    @override
    def collect(self, fragments: List[str]) -> dc.PredictionResult:
        if self._stats is None:
            raise ValueError("Stats should not be None")
        if self._model_info is None:
            raise ValueError("Model info should not be None")
        if self._load_model_config is None:
            raise ValueError("Load model config should not be None")
        if self._prediction_config is None:
            raise ValueError("Prediction config should not be None")
        return dc.PredictionResult(
            content="".join(fragments),
            stats=self._stats,
            model_info=self._model_info,
            load_config=self._load_model_config,
            prediction_config=self._prediction_config,
        )

    @override
    def result(self) -> dc.PredictionResult:
        """Get the final prediction results.

        If you have been streaming the results,
        calling this method will take no extra effort,
        as the results are already available in the internal buffer.

        Example:

        ```python
        prediction = model.complete(
            "When will The Winds of Winter be released?"
        )
        for fragment in prediction:
            print(fragment, end='', flush=True)
        result = prediction.result()
        print(result.stats)
        ```

        Returns:
            The final prediction results.
        ```
        """
        self.finished_event.wait()
        if self.status == "rejected":
            raise self.error
        if self.final_result is None:
            raise ValueError("Result is not available")
        return self.final_result

    @override
    def cancel(self) -> None:
        """Cancels the prediction.

        This will stop the prediction with stop reason `userStopped`.
        See LLMPredictionStopReason for other reasons
        that a prediction might stop.
        """
        self._on_cancel()
