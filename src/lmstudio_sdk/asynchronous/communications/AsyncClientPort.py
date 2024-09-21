import asyncio
import json
from .BaseClientPort import BaseClientPort

import websockets


class ClientPort(BaseClientPort):
    # TODO enums for allowable channel and rpc endpoints
    def __init__(self, uri: str, endpoint: str, identifier: str, passkey: str):
        super().__init__(uri, endpoint, identifier, passkey)
        self.running = False
        self.receive_task = None

    async def _connect(self):
        self._websocket = await websockets.connect(self.uri)
        await self._websocket.send(
            json.dumps(
                {
                    "authVersion": self._auth_version,
                    "clientIdentifier": self.identifier,
                    "clientPasskey": self._passkey,
                }
            )
        )
        self.running = True
        self.receive_task = asyncio.create_task(self.receive_messages())

    async def _close(self):
        self.running = False
        if self._websocket:
            await self._websocket.close()
        if self.receive_task:
            try:
                await asyncio.wait_for(self.receive_task, timeout=5.0)
            except asyncio.TimeoutError:
                print("Receive task did not complete in time")

    async def receive_messages(self):
        try:
            while self.running:
                assert self._websocket is not None
                message = await self._websocket.recv()
                data = json.loads(message)
                # FIXME debug
                print("Message received: ", data)

                # TODO: more robust data handling
                data_type = data.get("type", None)
                if data_type is None:
                    continue

                # channel endpoints
                # TODO: error handling
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
        except AssertionError:
            print("WebSocket connection not established in receive_messages: this should never happen?")
        except websockets.ConnectionClosedOK:
            print("WebSocket connection closed normally")
        except websockets.ConnectionClosedError as e:
            print(f"WebSocket connection closed with error: {e}")
        finally:
            self.running = False

    async def _send_payload(self, payload: dict):
        assert self._websocket is not None
        await self._websocket.send(json.dumps(payload))

    def _rpc_complete_event(self):
        return asyncio.Event()

    async def _call_rpc(self, payload: dict, complete: asyncio.Event, result: dict):
        assert self._websocket is not None
        await self._send_payload(payload)
        await complete.wait()
        return result


# TODO LLMPort, EmbeddingPort, SystemPort, DiagnosticsPort
