import json
import threading
import websocket
from typing import Dict
from .BaseClientPort import BaseClientPort


class PseudoFuture(threading.Event):
    def __init__(self):
        super().__init__()

    def set_result(self, result):
        self._result = result
        self.set()

    def set_exception(self, exception):
        self._exception = exception
        self.set()

    def result(self):
        self.wait()
        if hasattr(self, "_exception"):
            raise self._exception
        return self._result


class ClientPort(BaseClientPort):
    def __init__(self, uri: str, endpoint: str, identifier: str, passkey: str):
        super().__init__(uri, endpoint, identifier, passkey)
        self._lock = threading.Lock()
        self._connection_event = threading.Event()

    def on_message(self, ws, message):
        data = json.loads(message)
        # FIXME debug
        print("Message received: ", data)

        # TODO: more robust data handling
        data_type = data.get("type", None)
        if data_type is None:
            return

        # channel endpoints
        # TODO: error handling
        # TODO: un-asyncify handlers...
        if data_type == "channelSend":
            channel_id = data.get("channelId")
            if channel_id in self.channel_handlers:
                self.channel_handlers[channel_id](data.get("message", {}))
        elif data_type == "channelClose":
            channel_id = data.get("channelId")
            if channel_id in self.channel_handlers:
                del self.channel_handlers[channel_id]
        elif data_type == "channelError":
            channel_id = data.get("channelId")
            if channel_id in self.channel_handlers:
                self.channel_handlers[channel_id](data.get("error", {}))
                del self.channel_handlers[channel_id]

        # RPC endpoints
        # TODO currently we handle errors two semantic levels up whereas it should be one
        # implement error handling with the same semantics as channels
        elif data_type == "rpcResult" or data_type == "rpcError":
            call_id = data.get("callId", -1)
            # TODO we should pass only the error dict
            if call_id in self.rpc_handlers:
                self.rpc_handlers[call_id](data)
                del self.rpc_handlers[call_id]

    def on_error(self, ws, error):
        # TODO I'm pretty sure this is a WebSocket error not a message error
        pass

    def on_close(self, ws, close_status_code, close_msg):
        self._connection_event.clear()

    def on_open(self, ws):
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
        self._connection_event.set()

    def _connect(self) -> bool:
        # websocket.enableTrace(True)
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
            print("Failed to connect to WebSocket server")
            return False

        return True

    def _send_payload(self, payload: dict, extra: Dict | None):
        with self._lock:
            if self._websocket and self._connection_event.is_set():
                self._websocket.send(json.dumps(payload))
            else:
                print("Cannot send payload: websocket not connected")
            return extra

    def close(self) -> None:
        with self._lock:
            if self._websocket:
                self._websocket.close()

    def is_connected(self) -> bool:
        return self._connection_event.is_set()

    def _rpc_complete_event(self):
        return threading.Event()

    def promise_event(self):
        return PseudoFuture()

    # TODO type hint for return type
    def _call_rpc(self, payload: dict, complete: threading.Event, result: dict, extra: Dict | None):
        assert self._websocket is not None
        self._send_payload(payload)
        complete.wait()
        result = result.get("result", result)
        result.update({"extra": extra})
        return result


# TODO LLMPort, EmbeddingPort, SystemPort, DiagnosticsPort
