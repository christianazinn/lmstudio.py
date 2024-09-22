import threading
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict
from ...utils import get_logger, PseudoFuture, sync_async_decorator


logger = get_logger(__name__)


class BaseClientPort(ABC):
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
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def _send_payload(self, payload: dict, extra: dict | None):
        pass

    @abstractmethod
    def _call_rpc(self, payload: dict, complete: threading.Event | asyncio.Event, extra: dict | None):
        pass

    @abstractmethod
    def _rpc_complete_event(self) -> threading.Event | asyncio.Event:
        pass

    @abstractmethod
    def promise_event(self) -> asyncio.Future | PseudoFuture:
        pass

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

    def is_async(self):
        return asyncio.iscoroutinefunction(self._send_payload)

    # TODO endpoint enum
    # TODO: this is an absolutely atrocious design pattern with extra, figure it out
    @sync_async_decorator(obj_method="_send_payload", process_result=lambda x: x)
    def create_channel(
        self, endpoint: str, creation_parameter: Any | None, handler: Callable, extra: dict | None = None
    ) -> int:
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

        logger.debug(f"Creating channel to '{endpoint}' with ID {channel_id}. To see payload, enable SEND level logging.")

        return {"payload": payload, "extra": {"channel_id": channel_id, "extra": extra}}

    @sync_async_decorator(obj_method="_send_payload", process_result=lambda x: x)
    def send_channel_message(self, channel_id: int, message: dict):
        assert self._websocket is not None
        payload = {
            "type": "channelSend",
            "channelId": channel_id,
            "message": message,
        }
        logger.debug(f"Sending channel message on channel {channel_id}. To see payload, enable SEND level logging.")

        return {"payload": payload}

    # TODO type hint for return type
    # we implement this manually instead of using the decorator because of the different waiting models
    @sync_async_decorator(obj_method="_call_rpc", process_result=lambda x: x.get("result", x))
    def call_rpc(self, endpoint: str, parameter: Any | None, extra: dict | None = None):
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

        logger.debug(
            f"Sending RPC call to '{endpoint}' with call ID {call_id}. To see payload, enable SEND level logging."
        )

        return {
            "payload": payload,
            "complete": complete,
            "result": result,
            "extra": extra,
        }
