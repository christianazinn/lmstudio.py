import threading
from abc import ABC
from typing import Dict, Callable, Any
from ...common import sync_async_decorator


class BaseClientPort(ABC):
    _auth_version = 1
    __next_channel_id = 0
    __next_rpc_call_id = 0
    __channel_id_lock = threading.Lock()
    __rpc_call_id_lock = threading.Lock()

    def __init__(self, uri: str, endpoint: str, identifier: str, passkey: str):
        self.uri = uri + "/" + endpoint
        self.identifier = identifier
        self._passkey = passkey
        self._websocket = None
        self.channel_handlers: Dict[int, Callable] = {}
        self.rpc_handlers: Dict[int, Callable] = {}

    @classmethod
    def get_next_channel_id(cls):
        with cls.__channel_id_lock:
            channel_id = cls.__next_channel_id
            cls.__next_channel_id += 1
        return channel_id

    @classmethod
    def get_next_rpc_call_id(cls):
        with cls.__rpc_call_id_lock:
            call_id = cls.__next_rpc_call_id
            cls.__next_rpc_call_id += 1
        return call_id

    # TODO endpoint enum
    @sync_async_decorator(obj_method="_send_payload", process_result=lambda x: x)
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
        return {"payload": payload}

    @sync_async_decorator(obj_method="_send_payload", process_result=lambda x: x)
    def send_channel_message(self, channel_id: int, payload: dict):
        assert self._websocket is not None
        payload["channelId"] = channel_id
        return {"payload": payload}

    # TODO type hint for return type
    # we implement this manually instead of using the decorator because of the different waiting models
    @sync_async_decorator(obj_method="_call_rpc", process_result=lambda x: x.get("result", x))
    def call_rpc(self, endpoint: str, parameter: Any | None):
        assert self._websocket is not None
        result = {}

        # dependency injecting a complete event
        # TODO: type hinting, abstract method
        complete = self._rpc_complete_event()

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

        return {
            "payload": payload,
            "complete": complete,
            "result": result,
        }
