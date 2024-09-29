from typing import Callable, Literal, TypedDict

from ...utils import _assert, get_logger
from .BaseNamespace import BaseNamespace


logger = get_logger(__name__)


class DiagnosticsLogEventData(TypedDict):
    type: Literal["llm.prediction.input"]
    modelPath: str
    modelIdentifier: str
    input: str


class DiagnosticsLogEvent(TypedDict):
    timestamp: int
    data: DiagnosticsLogEventData


class DiagnosticsNamespace(BaseNamespace):
    def unstable_stream_logs(
        self, listener: Callable[[DiagnosticsLogEvent], None]
    ) -> Callable[[], None]:
        """
        Register a callback to receive log events. Return a function to stop receiving log events.

        This method is in alpha. Do not use this method in production yet.
        :alpha:
        """

        _assert(
            isinstance(listener, Callable),
            f"unstable_stream_logs: listener must be a callable, got {type(listener)}",
            logger,
        )

        def unsubscribe(channel_id: int) -> None:
            del self._port.channel_handlers[channel_id]
            return self._port.send_channel_message(
                channel_id, {"type": "channelClose"}
            )

        return self._port.create_channel(
            "streamLogs",
            None,
            listener,
            lambda x: (
                lambda: x.get("extra").get("unsubscribe")(x.get("channel_id"))
            ),
            extra={"unsubscribe": unsubscribe},
        )
