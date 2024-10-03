from __future__ import annotations
import asyncio
from abc import ABC
from typing import Any, AsyncIterator, Callable, List, Optional
from typing_extensions import override

import lmstudio_sdk.dataclasses as dc

from .BaseOngoingPrediction import (
    BaseOngoingPrediction,
    BaseStreamableIterator,
    TFinal,
    TFragment,
)


class StreamablePromise(BaseStreamableIterator[TFragment, TFinal], ABC):
    """An abstract streamable async iterator that can be awaited on."""

    def __init__(self, on_cancel: Callable[[], None]):
        super().__init__(on_cancel)
        self.queue: asyncio.Queue[Optional[TFragment]] = asyncio.Queue()
        self.promise_final: asyncio.Future[TFinal] = asyncio.Future()

    @override
    def push(self, fragment: TFragment) -> None:
        if self.status != "pending":
            return
        self.buffer.append(fragment)
        self.queue.put_nowait(fragment)

    @override
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

    @override
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


class AsyncOngoingPrediction(
    StreamablePromise[str, dc.PredictionResult],
    BaseOngoingPrediction[str, dc.PredictionResult],
):
    """
    Represents an ongoing prediction.

    This resolves to a PredictionResult, which contains the generated text
    in the `.content` property.

    Example usage:

    ```python
    completion = await model.complete(
        "When will The Winds of Winter be released?"
    )
    result = await completion.result()
    print(result.content)
    ```

    You can also await directly on the completion object, resulting
    in a bit of an awkward syntax:

    ```python
    result = await (await model.complete(
        "When will The Winds of Winter be released?"
    ))
    print(result.content)
    ```

    Alternatively, you can stream the result
    (process the results as more content is being generated):

    ```python
    async for fragment in model.complete(
        "When will The Winds of Winter be released?"
    ):
        print(fragment, end='', flush=True)
    ```
    """

    @override
    async def collect(self, fragments: List[str]) -> dc.PredictionResult:
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
    def result(self) -> asyncio.Future[dc.PredictionResult]:
        """Get the final prediction results.

        If you have been streaming the results,
        awaiting on this method will take no extra effort,
        as the results are already available in the internal buffer.

        Example:

        ```python
        prediction = await model.complete(
            "When will The Winds of Winter be released?"
        )
        async for fragment in prediction:
            print(fragment, end='', flush=True)
        result = await prediction.result()
        print(result.stats)
        ```

        Returns:
            The final prediction results.
        ```
        """
        return self.promise_final

    @override
    async def cancel(self) -> None:
        """Cancels the prediction.

        This will stop the prediction with stop reason `userStopped`.
        See LLMPredictionStopReason for other reasons
        that a prediction might stop.
        """
        await self._on_cancel()
