import json
import threading
import websocket
from typing import Callable, Dict, Any


auth_version = 1


class ClientPort:
    _next_channel_id = 0
    _next_rpc_call_id = 0
    _channel_id_lock = threading.Lock()
    _rpc_call_id_lock = threading.Lock()

    def __init__(self, uri: str, endpoint: str, identifier: str, passkey: str):
        self.uri = uri + "/" + endpoint
        self.identifier = identifier
        self._passkey = passkey
        self._websocket = None
        self.channel_handlers: Dict[int, Callable] = {}
        self.rpc_handlers: Dict[int, Callable] = {}
        self._lock = threading.Lock()
        self._connection_event = threading.Event()

    @classmethod
    def get_next_channel_id(cls):
        with cls._channel_id_lock:
            channel_id = cls._next_channel_id
            cls._next_channel_id += 1
        return channel_id

    @classmethod
    def get_next_rpc_call_id(cls):
        with cls._rpc_call_id_lock:
            call_id = cls._next_rpc_call_id
            cls._next_rpc_call_id += 1
        return call_id

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
                    "authVersion": auth_version,
                    "clientIdentifier": self.identifier,
                    "clientPasskey": self._passkey,
                }
            )
        )
        self._connection_event.set()

    def connect(self) -> bool:
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

    def _send_payload(self, payload: dict) -> None:
        with self._lock:
            if self._websocket and self._connection_event.is_set():
                self._websocket.send(json.dumps(payload))
            else:
                print("Cannot send payload: websocket not connected")

    def close(self) -> None:
        with self._lock:
            if self._websocket:
                self._websocket.close()

    def is_connected(self) -> bool:
        return self._connection_event.is_set()

    # TODO: endpoint enum
    def create_channel(self, endpoint: str, creation_parameter: Any | None, handler: Callable) -> int:
        assert self._websocket is not None
        channel_id = self.get_next_channel_id()
        payload = {
            "type": "channelCreate",
            "endpoint": endpoint,
            "channelId": channel_id,
        }
        if creation_parameter is not None:
            payload["creationParameter"] = creation_parameter
        self.channel_handlers[channel_id] = handler

        self._send_payload(payload)
        return channel_id

    def send_channel_message(self, channel_id: int, payload: dict):
        assert self._websocket is not None
        payload["channelId"] = channel_id
        self._send_payload(payload)

    # TODO type hint for return type
    def call_rpc(self, endpoint: str, parameter: Any | None):
        assert self._websocket is not None

        complete = threading.Event()
        result = {}

        def rpc_handler(data):
            nonlocal result
            result.update(data)
            complete.set()

        call_id = self.get_next_rpc_call_id()
        payload = {
            "type": "rpcCall",
            "endpoint": endpoint,
            "callId": call_id,
        }
        if parameter is not None:
            payload["parameter"] = parameter
        self.rpc_handlers[call_id] = rpc_handler

        self._send_payload(payload)
        complete.wait()

        return result.get("result", result)


# TODO LLMPort, EmbeddingPort, SystemPort, DiagnosticsPort
