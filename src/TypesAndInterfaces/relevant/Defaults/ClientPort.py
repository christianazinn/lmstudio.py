import asyncio
import json
import threading
from typing import Callable, Dict

import websockets


class ClientPort:
    _next_channel_id = 0
    _next_rpc_call_id = 0
    _channel_id_lock = threading.Lock()
    _rpc_call_id_lock = threading.Lock()

    def __init__(self, uri: str):
        self.uri = uri
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
                    "authVersion": 1,
                    "clientIdentifier": "pytest",
                    "clientPasskey": "pytest",
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
                print("Message received: ", data)

                # TODO: more robust data handling
                if "type" in data:
                    # channel endpoints
                    if data["type"] == "channelSend":
                        channel_id = data["channelId"]
                        if channel_id in self.channel_handlers:
                            await self.channel_handlers[channel_id](data["message"])
                    elif data["type"] == "channelClose":
                        channel_id = data["channelId"]
                        if channel_id in self.channel_handlers:
                            del self.channel_handlers[channel_id]
                    elif data["type"] == "channelError":
                        channel_id = data["channelId"]
                        if channel_id in self.channel_handlers:
                            await self.channel_handlers[channel_id](data["error"])
                            del self.channel_handlers[channel_id]

                    # RPC endpoints
                    elif data["type"] == "rpcResult" or data["type"] == "rpcError":
                        call_id = data["callId"]
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

    # TODO: endpoint enum
    async def create_channel(self, endpoint: str, creation_parameter: dict, handler: Callable) -> int:
        assert self.websocket is not None
        channel_id = self.get_next_channel_id()
        payload = {
            "type": "channelCreate",
            "endpoint": endpoint,
            "channelId": channel_id,
            "creationParameter": creation_parameter,
        }
        self.channel_handlers[channel_id] = handler
        await self.websocket.send(json.dumps(payload))
        return channel_id

    # TODO type hint for return type
    async def call_rpc(self, endpoint: str, parameter: dict):
        assert self.websocket is not None

        # TODO make sure this works!
        # TODO parameter validation
        complete = asyncio.Event()
        result = {}

        async def rpc_handler(data):
            result.update(data["result"])
            complete.set()

        call_id = self.get_next_rpc_call_id()
        payload = {
            "type": "rpcCall",
            "endpoint": endpoint,
            "callId": call_id,
            "parameter": parameter,
        }
        self.rpc_handlers[call_id] = rpc_handler

        await self.websocket.send(json.dumps(payload))
        await complete.wait()
        return result
