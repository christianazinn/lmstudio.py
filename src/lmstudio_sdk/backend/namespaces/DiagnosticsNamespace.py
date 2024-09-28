from typing import Callable, Literal, TypedDict


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

    def connect(self):
        return self._port.connect()

    def close(self):
        return self._port.close()

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
