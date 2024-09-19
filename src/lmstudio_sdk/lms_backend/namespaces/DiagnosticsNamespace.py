from typing import Literal, Callable, TypedDict


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
        self.__port = port

    def connect(self) -> None:
        self.__port.connect()

    def close(self) -> None:
        self.__port.close()

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
