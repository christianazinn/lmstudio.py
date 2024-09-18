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
        self.__port = port  # Type not specified in TypeScript

    async def connect(self) -> None:
        await self.__port.connect()

    async def close(self) -> None:
        await self.__port.close()

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
