from typing import Callable, Literal, TypedDict

from ..communications import BaseClientPort
from .BaseNamespace import BaseNamespace


class DiagnosticsLogEventData(TypedDict):
    type: Literal["llm.prediction.input"]
    modelPath: str
    modelIdentifier: str
    input: str


class DiagnosticsLogEvent(TypedDict):
    timestamp: int
    data: DiagnosticsLogEventData


class DiagnosticsNamespace(BaseNamespace[BaseClientPort]):
    def unstable_stream_logs(self, listener: Callable[[DiagnosticsLogEvent], None]) -> Callable[[], None]:
        """
        Register a callback to receive log events. Return a function to stop receiving log events.

        This method is in alpha. Do not use this method in production yet.
        :alpha:
        """

        def unsubscribe(channel_id: int) -> None:
            del self._port.channel_handlers[channel_id]
            return self._port.send_channel_message(channel_id, {"type": "channelClose"})

        return self._port.create_channel(
            "streamLogs",
            None,
            listener,
            lambda x: (lambda: x.get("extra").get("unsubscribe")(x.get("channel_id"))),
            extra={"unsubscribe": unsubscribe},
        )
