import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

import lmstudio_sdk.utils as utils


logger = utils.get_logger(__name__)


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
    def _send_payload(
        self,
        payload: dict,
        extra: Optional[dict] = None,
        postprocess: Optional[Callable[[dict], Any]] = None,
    ):
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
        pass

    @abstractmethod
    def _rpc_complete_event(self) -> threading.Event | asyncio.Event:
        pass

    @abstractmethod
    def _promise_event(self) -> asyncio.Future | utils.PseudoFuture:
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

    def is_async(self):
        return asyncio.iscoroutinefunction(self._send_payload)

    def create_channel(
        self,
        endpoint: str,
        creation_parameter: Optional[dict],
        handler: Callable,
        postprocess: Callable[[dict], Any],
        extra: Optional[dict] = None,
    ) -> int:
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
