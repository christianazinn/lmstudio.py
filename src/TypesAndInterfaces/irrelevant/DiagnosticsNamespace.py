from typing import Literal, Callable
from TypesAndInterfaces.relevant.Defaults.ConfiguredBaseModel import ConfiguredBaseModel


class DiagnosticsLogEventData(ConfiguredBaseModel):
    type: Literal["llm.prediction.input"]
    modelPath: str
    modelIdentifier: str
    input: str


class DiagnosticsLogEvent(ConfiguredBaseModel):
    timestamp: int
    data: DiagnosticsLogEventData


class DiagnosticsNamespace:
    def __init__(self):
        self._diagnosticsPort = None  # Type not specified in TypeScript
        self._validator = None  # Type not specified in TypeScript

    """
    Register a callback to receive log events. Return a function to stop receiving log events.

    This method is in alpha. Do not use this method in production yet.
    @alpha
    """

    def unstable_stream_logs(self, listener: Callable[[DiagnosticsLogEvent], None]) -> Callable[[], None]:
        # TODO implement
        def unsubscribe() -> None:
            # Logic to stop receiving log events
            pass

        return unsubscribe
