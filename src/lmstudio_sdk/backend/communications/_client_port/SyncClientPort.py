import json
import threading
import websocket
from typing import Any, Callable, Optional
from typing_extensions import override

import lmstudio_sdk.utils as utils

from .BaseClientPort import BaseClientPort


logger = utils.get_logger(__name__)


class SyncClientPort(BaseClientPort):
    """Synchronous client port for LM Studio communication.

    See `BaseClientPort` for more information.
    """

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
        self._handle_data(data)

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

    @override
    def connect(self):
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

        if self._connection_event.wait(timeout=5):
            logger.websocket("Connected to WebSocket at %s.", self.uri)
        else:
            logger.error(
                "Failed to connect to WebSocket server at %s.", self.uri
            )

    @override
    def close(self):
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

    @override
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

    @override
    def _rpc_complete_event(self):
        return threading.Event()

    @override
    def _promise_event(self):
        return utils.PseudoFuture()

    @override
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
