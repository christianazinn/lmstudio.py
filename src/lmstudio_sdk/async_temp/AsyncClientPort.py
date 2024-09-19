import asyncio
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Any

import websockets


auth_version = 1


class ClientPort:
    _next_channel_id = 0
    _next_rpc_call_id = 0
    _channel_id_lock = threading.Lock()
    _rpc_call_id_lock = threading.Lock()

    # TODO enums for allowable channel and rpc endpoints
    def __init__(self, uri: str, endpoint: str, identifier: str, passkey: str):
        self.uri = uri + "/" + endpoint
        self.identifier = identifier
        self.passkey = passkey
        self.websocket = None
        self.channel_handlers: Dict[int, Callable] = {}
        self.rpc_handlers: Dict[int, Callable] = {}
        self.running = False
        self.receive_task = None

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

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        await self.websocket.send(
            json.dumps(
                {
                    "authVersion": auth_version,
                    "clientIdentifier": self.identifier,
                    "clientPasskey": self.passkey,
                }
            )
        )
        self.running = True
        self.receive_task = asyncio.create_task(self.receive_messages())

    async def close(self):
        self.running = False
        if self.websocket:
            await self.websocket.close()
        if self.receive_task:
            try:
                await asyncio.wait_for(self.receive_task, timeout=5.0)
            except asyncio.TimeoutError:
                print("Receive task did not complete in time")

    async def receive_messages(self):
        try:
            while self.running:
                assert self.websocket is not None
                message = await self.websocket.recv()
                data = json.loads(message)
                # FIXME debug
                # print("Message received: ", data)

                # TODO: more robust data handling
                data_type = data.get("type", None)
                if data_type is None:
                    continue

                # channel endpoints
                # TODO: error handling
                if data_type == "channelSend":
                    channel_id = data.get("channelId")
                    if channel_id in self.channel_handlers:
                        await self.channel_handlers[channel_id](data.get("message", {}))
                elif data_type == "channelClose":
                    channel_id = data.get("channelId")
                    if channel_id in self.channel_handlers:
                        del self.channel_handlers[channel_id]
                elif data_type == "channelError":
                    channel_id = data.get("channelId")
                    if channel_id in self.channel_handlers:
                        await self.channel_handlers[channel_id](data.get("error", {}))
                        del self.channel_handlers[channel_id]

                # RPC endpoints
                # TODO currently we handle errors two semantic levels up whereas it should be one
                # implement error handling with the same semantics as channels
                elif data_type == "rpcResult" or data_type == "rpcError":
                    call_id = data.get("callId", -1)
                    # TODO we should pass only the error dict
                    if call_id in self.rpc_handlers:
                        await self.rpc_handlers[call_id](data)
                        del self.rpc_handlers[call_id]
        except AssertionError:
            print("WebSocket connection not established in receive_messages: this should never happen?")
        except websockets.ConnectionClosedOK:
            print("WebSocket connection closed normally")
        except websockets.ConnectionClosedError as e:
            print(f"WebSocket connection closed with error: {e}")
        finally:
            self.running = False

    async def __send_payload(self, payload: dict):
        assert self.websocket is not None
        await self.websocket.send(json.dumps(payload))

    # TODO: endpoint enum
    # TODO: ensure handler is async
    async def create_channel(self, endpoint: str, creation_parameter: Any | None, handler: Callable) -> int:
        assert self.websocket is not None
        channel_id = self.get_next_channel_id()
        payload = {
            "type": "channelCreate",
            "endpoint": endpoint,
            "channelId": channel_id,
        }
        if creation_parameter is not None:
            payload["creationParameter"] = creation_parameter
        self.channel_handlers[channel_id] = handler

        await self.__send_payload(payload)
        return channel_id

    async def send_channel_message(self, channel_id: int, payload: dict):
        assert self.websocket is not None
        payload["channelId"] = channel_id
        await self.__send_payload(payload)

    # TODO type hint for return type
    # from experience: making this synchronous is more trouble than worth
    async def call_rpc(self, endpoint: str, parameter: Any | None):
        assert self.websocket is not None

        complete = asyncio.Event()
        result = {}

        async def rpc_handler(data):
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

        await self.websocket.send(json.dumps(payload))
        await complete.wait()
        # Send the payload asynchronously

        return result.get("result", result)


# TODO LLMPort, EmbeddingPort, SystemPort, DiagnosticsPort
