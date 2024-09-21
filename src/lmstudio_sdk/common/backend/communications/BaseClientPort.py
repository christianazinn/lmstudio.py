import threading
from abc import ABC
from typing import Dict, Callable


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
        self.websocket = None
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

    # TODO: figure out how to reuse more code
