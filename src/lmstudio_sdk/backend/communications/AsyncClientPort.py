import asyncio
import json
import websockets
from typing import Any, Callable

from .BaseClientPort import BaseClientPort
from ...utils import get_logger, pretty_print, pretty_print_error, RPCError


logger = get_logger(__name__)


class AsyncClientPort(BaseClientPort):
    # TODO enums for allowable channel and rpc endpoints
    def __init__(self, uri: str, endpoint: str, identifier: str, passkey: str):
        super().__init__(uri, endpoint, identifier, passkey)
        self.running = False
        self.receive_task = None

    async def connect(self):
        logger.websocket(f"Connecting to WebSocket at {self.uri}...")
        self._websocket = await websockets.connect(self.uri)
        logger.websocket(f"Connected to WebSocket at {self.uri}. Sending authentication packet as {self.identifier}...")
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
        logger.websocket(f"Async port {self.endpoint} is authenticated. Establishing receive task.")
        self.receive_task = asyncio.create_task(self.receive_messages())

    async def close(self):
        self.running = False
        if self._websocket:
            logger.websocket(f"Closing WebSocket connection on async port {self.endpoint}...")
            await self._websocket.close()
            logger.websocket(f"WebSocket connection closed to {self.endpoint}.")
        if self.receive_task:
            try:
                logger.websocket(f"Waiting for receive task to time out on async port {self.endpoint}...")
                await asyncio.wait_for(self.receive_task, timeout=5.0)
                logger.websocket(f"Receive task timed out on async port {self.endpoint}.")
            except asyncio.TimeoutError:
                logger.error(f"Receive task did not complete in time on async port {self.endpoint}!")

    async def receive_messages(self):
        try:
            while self.running:
                assert self._websocket is not None
                logger.recv(f"Waiting for message on async port {self.endpoint}.")
                message = await self._websocket.recv()
                data = json.loads(message)
                logger.recv(f"Message received on async port {self.endpoint}:\n{pretty_print(data)}")

                # TODO: more robust data handling
                data_type = data.get("type", None)
                if data_type is None:
                    continue

                # channel endpoints
                if data_type == "channelSend":
                    channel_id = data.get("channelId")
                    if channel_id in self.channel_handlers:
                        self.channel_handlers[channel_id](data.get("message", data))
                elif data_type == "channelClose":
                    channel_id = data.get("channelId")
                    if channel_id in self.channel_handlers:
                        del self.channel_handlers[channel_id]
                elif data_type == "channelError":
                    channel_id = data.get("channelId")
                    if channel_id in self.channel_handlers:
                        self.channel_handlers[channel_id](data)
                        del self.channel_handlers[channel_id]

                # RPC endpoints
                # TODO: error handling
                elif data_type == "rpcResult" or data_type == "rpcError":
                    call_id = data.get("callId", -1)
                    if call_id in self.rpc_handlers:
                        self.rpc_handlers[call_id](data)
                        del self.rpc_handlers[call_id]
        except AssertionError:
            logger.error(
                f"WebSocket connection to {self.uri} not established in receive_messages: this should never happen?"
            )
        except websockets.ConnectionClosedOK:
            logger.websocket(f"WebSocket connection to {self.uri} closed normally.")
        except websockets.ConnectionClosedError as e:
            logger.error(f"WebSocket connection closed with error: {e}")
        finally:
            self.running = False

    async def _send_payload(
        self, payload: dict, extra: dict | None = None, callback: Callable[[dict], Any] | None = None
    ):
        if not self._websocket:
            logger.error("Attempted to send payload, but WebSocket connection is not established.")
            raise ValueError("WebSocket connection not established.")
        logger.send(f"Sending payload on async port {self.endpoint}:\n{pretty_print(payload)}")
        await self._websocket.send(json.dumps(payload))
        if callback:
            return callback(extra)
        return extra

    def _rpc_complete_event(self):
        return asyncio.Event()

    def promise_event(self):
        return asyncio.Future()

    async def _call_rpc(
        self,
        payload: dict,
        complete: asyncio.Event,
        result: dict,
        callback: Callable[[dict], Any],
        extra: dict | None = None,
    ):
        await self._send_payload(payload)
        logger.debug(
            f"Waiting for RPC call to {payload.get('endpoint', 'unknown - enable WRAPPER level logging')} to complete..."
        )
        await complete.wait()

        if "error" in result:
            logger.error(f"Error in RPC call: {pretty_print_error(result.get('error'))}")
            raise RPCError(f"Error in RPC call: {result.get('error').get('title', 'Unknown error')}")

        result = result.get("result", result)
        if isinstance(result, dict):
            result.update({"extra": extra})
        else:
            result = {"result": result, "extra": extra}

        def process_result(x):
            if isinstance(x, dict):
                return x.get("result", x)
            return x

        return process_result(callback(result))


# TODO LLMPort, EmbeddingPort, SystemPort, DiagnosticsPort
