from typing import Literal, Callable, TypedDict

from ...common import sync_async_decorator


class DiagnosticsLogEventData(TypedDict):
    type: Literal["llm.prediction.input"]
    modelPath: str
    modelIdentifier: str
    input: str


class DiagnosticsLogEvent(TypedDict):
    timestamp: int
    data: DiagnosticsLogEventData


class DiagnosticsNamespace:
    def __init__(self, port):
        self._port = port

    @sync_async_decorator(obj_method="_connect", process_result=lambda x: None)
    def connect(self):
        pass

    @sync_async_decorator(obj_method="_close", process_result=lambda x: None)
    def close(self):
        pass

    # TODO make me work
    def unstable_stream_logs(self, listener: Callable[[DiagnosticsLogEvent], None]) -> Callable[[], None]:
        """
        Register a callback to receive log events. Return a function to stop receiving log events.

        This method is in alpha. Do not use this method in production yet.
        :alpha:
        """

        # TODO implement
        def unsubscribe() -> None:
            # Logic to stop receiving log events
            pass

        return unsubscribe
