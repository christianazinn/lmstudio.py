import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

import lmstudio_sdk.utils as utils


logger = utils.get_logger(__name__)


class BaseClientPort(ABC):
    """Abstract class describing a client port for LM Studio communication.

    Not part of the public API, but worth documenting. This class outlines
    the internal API for communication with the server, since we use two
    different backends: `websocket-client` for synchronous communication
    and `websockets` for asynchronous communication.

    This class handles common functionality (e.g. handling call IDs)
    and defines the `create_channel`, `send_channel_message`,
    and `call_rpc` methods that should be used by other code
    to interact with the server.

    The current communications framework uses `postprocess` callbacks
    to process responses from the server, which is a bit of a hack
    to allow the same public API methods to function both synchronously
    and asynchronously. This is not a very good design pattern!

    It works fine for e.g. RPC calls where all we need to do is
    extract a particular field from the response, but for channel methods
    where we need to tie abort callbacks to the channel ID (which is not
    determined until after the call is made), it's a bit of a mess.

    Attributes:
        uri: Full URI for the client connection.
        endpoint: Endpoint for the client, e.g. "llm".
        identifier: Unique identifier for the client.
        _passkey: Passkey for the client.
        _websocket: WebSocket instance (will differ by backend).
        channel_handlers: Handler callbacks for channel messages.
        rpc_handlers: Handler callbacks for RPC calls.
    """

    _auth_version = 1
    __next_channel_id = 0
    __next_rpc_call_id = 0
    __channel_id_lock = threading.Lock()
    __rpc_call_id_lock = threading.Lock()

    def __init__(self, uri: str, endpoint: str, identifier: str, passkey: str):
        self.uri = uri + "/" + endpoint
        self.endpoint = endpoint
        self.identifier = identifier
        self._passkey = passkey
        self._websocket = None
        self.channel_handlers: Dict[int, Callable] = {}
        self.rpc_handlers: Dict[int, Callable] = {}

    @abstractmethod
    def connect(self):
        """Connect to the server on all ports."""
        pass

    @abstractmethod
    def close(self):
        """Close the connection to the server on all ports."""
        pass

    @abstractmethod
    def _send_payload(
        self,
        payload: dict,
        extra: Optional[dict] = None,
        postprocess: Optional[Callable[[dict], Any]] = None,
    ):
        """Send a JSON message to the server over the backend.

        Should be the only method that directly interacts with the
        backend's WebSocket implementation.

        Args:
            payload: JSON payload to send.
            extra: Arguments to `postprocess`. Useful for e.g. passing
                channel IDs to abort callbacks.
            postprocess: Callback to process the response.
                Will be called on the response from the server,
                and should return the desired result. Should be
                propagated all the way from the public API method
                at the top of the call stack.

        Returns:
            The result of the `postprocess` callback on `extra`.
        """
        pass

    @abstractmethod
    def _call_rpc(
        self,
        payload: dict,
        complete: threading.Event | asyncio.Event,
        result: dict,
        postprocess: Callable[[dict], Any],
        extra: Optional[dict],
    ):
        """Backend: send an RPC to the server.

        Backend implementation of `call_rpc`, which should be used in the
        internal API, so must be implemented on a per-backend basis.

        Args:
            payload: JSON payload to send.
            complete: Event to set when the RPC completes.
            result: Dictionary to store the result of the RPC.
            postprocess: Callback to process the response. Not to be confused
                with the `postprocess` argument to `_send_payload`.
            extra: Extra data to `postprocess`.

        Returns:
            The result of the RPC, after postprocessing.
        """
        pass

    @abstractmethod
    def _rpc_complete_event(self) -> threading.Event | asyncio.Event:
        """Dependency inject a complete event."""
        pass

    @abstractmethod
    def _promise_event(self) -> asyncio.Future | utils.PseudoFuture:
        """Dependency inject a Future-like."""
        pass

    @classmethod
    def __get_next_channel_id(cls):
        with cls.__channel_id_lock:
            channel_id = cls.__next_channel_id
            cls.__next_channel_id += 1
        return channel_id

    @classmethod
    def __get_next_rpc_call_id(cls):
        with cls.__rpc_call_id_lock:
            call_id = cls.__next_rpc_call_id
            cls.__next_rpc_call_id += 1
        return call_id

    def _handle_data(self, data: dict):
        """Handle an incoming packet from the server.

        Used in message receipt loops to process incoming messages.

        Args:
            data: JSON data from the server.
        """
        data_type = data.get("type", None)
        if data_type is None:
            return

        # channel endpoints
        if data_type == "channelSend":
            channel_id = data.get("channelId")
            if channel_id in self.channel_handlers:
                message_content = data.get("message", data)
                if message_content.get("type", None) == "log":
                    message_content = message_content.get("log")
                self.channel_handlers[channel_id](message_content)
        elif data_type == "channelClose":
            channel_id = data.get("channelId")
            if channel_id in self.channel_handlers:
                del self.channel_handlers[channel_id]
        elif data_type == "channelError":
            channel_id = data.get("channelId")
            if channel_id in self.channel_handlers:
                self.channel_handlers[channel_id](data)
                del self.channel_handlers[channel_id]

        # RPC endpoints
        elif data_type == "rpcResult" or data_type == "rpcError":
            call_id = data.get("callId", -1)
            if call_id in self.rpc_handlers:
                self.rpc_handlers[call_id](data)
                del self.rpc_handlers[call_id]

    def is_async(self):
        return asyncio.iscoroutinefunction(self._send_payload)

    def create_channel(
        self,
        endpoint: str,
        creation_parameter: Optional[dict],
        handler: Callable,
        postprocess: Callable[[dict], Any],
        extra: Optional[dict] = None,
    ):
        """Create a channel to the server.

        This returns as soon as the channel has been established
        and postprocessing completed. In practice this means that
        `postprocess` should do no more than e.g. register
        abort callbacks.

        Args:
            endpoint: Endpoint to create the channel to.
            creation_parameter: Parameters to pass to the channel creation.
            handler: Callback to handle incoming messages on the channel.
            postprocess: Callback to process the response.
            extra: Extra data to pass to `postprocess`.

        Returns:
            The result of the `postprocess` callback on the channel ID
            and `extra`, after sending the channel creation packet.
        """
        assert self._websocket is not None
        channel_id = self.__get_next_channel_id()
        payload = {
            "type": "channelCreate",
            "endpoint": endpoint,
            "channelId": channel_id,
        }
        if creation_parameter is not None:
            payload["creationParameter"] = creation_parameter
        self.channel_handlers[channel_id] = handler

        logger.debug(
            "Creating channel to '%s' with ID %d. \
            To see payload, enable SEND level logging.",
            endpoint,
            channel_id,
        )

        return self._send_payload(
            payload,
            extra={"channelId": channel_id, "extra": extra},
            postprocess=postprocess,
        )

    def send_channel_message(self, channel_id: int, message: dict):
        """Send a message on a channel.

        In practice this is just for cancelling channel operations
        like model loading and inference.

        Args:
            channel_id: ID of the channel to send the message on.
            message: Message to send on the channel.
        """
        assert self._websocket is not None
        payload = {
            "type": "channelSend",
            "channelId": channel_id,
            "message": message,
        }
        logger.debug(
            "Sending channel message on channel %d. \
            To see payload, enable SEND level logging.",
            channel_id,
        )

        return self._send_payload(payload)

    def call_rpc(
        self,
        endpoint: str,
        parameter: Any,
        postprocess: Callable[[dict], Any],
        extra: Optional[dict] = None,
    ):
        """Send an RPC to the server.

        Will block until the RPC completes, then return the desired
        result as specified by calling `postprocess` on the response.

        This should actually not block in the async case, but it does:
        needs to be fixed.

        Args:
            endpoint: Endpoint to send the RPC to.
            parameter: Parameters to pass to the RPC.
            postprocess: Callback to process the response.
            extra: Extra data to pass to `postprocess`.

        Returns:
            The result of the `postprocess` callback on the RPC result.
        """
        assert self._websocket is not None
        result = {}

        # dependency injecting a complete event
        complete = self._rpc_complete_event()

        def rpc_handler(data):
            nonlocal result
            result.update(data)
            complete.set()

        call_id = self.__get_next_rpc_call_id()
        payload = {
            "type": "rpcCall",
            "endpoint": endpoint,
            "callId": call_id,
        }
        if parameter is not None:
            payload["parameter"] = parameter
        self.rpc_handlers[call_id] = rpc_handler

        logger.debug(
            "Sending RPC call to '%s' with call ID %d. \
            To see payload, enable SEND level logging.",
            endpoint,
            call_id,
        )

        return self._call_rpc(payload, complete, result, postprocess, extra)
