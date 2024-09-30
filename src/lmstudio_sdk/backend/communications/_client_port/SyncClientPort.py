import json
import threading
import websocket
from typing import Any, Callable, Optional

import lmstudio_sdk.utils as utils

from .BaseClientPort import BaseClientPort


logger = utils.get_logger(__name__)


class SyncClientPort(BaseClientPort):
    def __init__(self, uri: str, endpoint: str, identifier: str, passkey: str):
        super().__init__(uri, endpoint, identifier, passkey)
        self._lock = threading.Lock()
        self._connection_event = threading.Event()

    def on_message(self, ws, message):
        data = json.loads(message)
        logger.recv(
            "Message received on sync port %s:\n%s",
            self.endpoint,
            utils.pretty_print(data),
        )

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

    def on_error(self, ws, error):
        logger.error(
            "Error in WebSocket connection to %s: %s", self.uri, str(error)
        )

    def on_close(self, ws, close_status_code, close_msg):
        self._connection_event.clear()

    def on_open(self, ws):
        logger.websocket(
            "Sending authentication packet to %s as %s...",
            self.uri,
            self.identifier,
        )
        # auth handshake
        self._websocket.send(
            json.dumps(
                {
                    "authVersion": self._auth_version,
                    "clientIdentifier": self.identifier,
                    "clientPasskey": self._passkey,
                }
            )
        )
        logger.websocket("Sync port authenticated: %s.", self.endpoint)
        self._connection_event.set()

    def connect(self) -> bool:
        with self._lock:
            self._websocket = websocket.WebSocketApp(
                self.uri,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open,
            )
        wst = threading.Thread(target=self._websocket.run_forever)
        wst.daemon = True
        wst.start()

        if not self._connection_event.wait(timeout=5):
            logger.error(
                "Failed to connect to WebSocket server at %s.", self.uri
            )
            return False

        logger.websocket("Connected to WebSocket at %s.", self.uri)
        return True

    def _send_payload(
        self,
        payload: dict,
        extra: Optional[dict] = None,
        postprocess: Optional[Callable[[dict], Any]] = None,
    ):
        with self._lock:
            if self._websocket and self._connection_event.is_set():
                logger.send(
                    "Sending payload on sync port %s:\n%s",
                    self.endpoint,
                    utils.pretty_print(payload),
                )
                self._websocket.send(json.dumps(payload))
            else:
                logger.error(
                    "Attempted to send payload, \
                    but WebSocket connection is not established."
                )
                raise ValueError("WebSocket connection is not established.")
            if postprocess:
                return postprocess(extra)
            return extra

    def close(self) -> None:
        with self._lock:
            if self._websocket:
                logger.websocket(
                    "Closing WebSocket connection on sync port %s.",
                    self.endpoint,
                )
                self._websocket.close()
                logger.websocket(
                    "WebSocket connection closed to %s.", self.endpoint
                )

    def is_connected(self) -> bool:
        return self._connection_event.is_set()

    def _rpc_complete_event(self):
        return threading.Event()

    def _promise_event(self):
        return utils.PseudoFuture()

    def _call_rpc(
        self,
        payload: dict,
        complete: threading.Event,
        result: dict,
        postprocess: Callable[[dict], Any],
        extra: Optional[dict] = None,
    ):
        assert self._websocket is not None
        self._send_payload(payload)
        logger.debug(
            "Waiting for RPC call to complete to %s...",
            payload.get("endpoint", "unknown"),
        )
        complete.wait()

        if "error" in result:
            logger.error(
                "Error in RPC call: %s",
                utils.pretty_print_error(result.get("error")),
            )
            raise utils.RPCError(
                "Error in RPC call: %s",
                result.get("error").get("title", "Unknown error"),
            )

        result = result.get("result", result)
        if isinstance(result, dict):
            result.update({"extra": extra})
        else:
            result = {"result": result, "extra": extra}

        def process_result(x):
            if isinstance(x, dict):
                return x.get("result", x)
            return x

        return process_result(postprocess(result))
